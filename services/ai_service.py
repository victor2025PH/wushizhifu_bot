"""
AI Service for handling OpenAI and Gemini API calls with automatic fallback
"""
import os
import logging
from typing import Optional, List, Dict
from config import Config

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI chat functionality with OpenAI (priority) and Gemini (fallback)"""
    
    # Knowledge base content
    KNOWLEDGE_BASE = """
你是伍拾支付（WuShiPay）的智能客服助手。伍拾支付是 Telegram 生態中領先的數字資產支付解決方案提供商。

公司核心優勢：
- 99.9% 交易成功率
- 金融級資金安全（多重簽名冷錢包）
- 7×24小時 1對1 專屬客服
- 極速到賬，毫秒級響應

主要功能：
- 支付寶/微信支付通道
- USDT 充值提現
- 匯率計算器
- 交易記錄查詢
- 統計信息查看

常見問題：
- 如何充值：在"我的錢包"頁面查看 USDT 充值地址，向該地址轉入 USDT 即可
- 如何提現：在"我的錢包"頁面選擇提現，輸入提現地址和金額
- 提現時間：通常 1-3 個工作日內到賬
- 費率：根據用戶 VIP 等級收取不同費率，可在計算器中查看
- 客服聯繫：Telegram @wushizhifu_jianglai

請以友好、專業、簡潔的方式回答用戶問題。如果無法回答或需要人工協助，請明確告知用戶可以點擊"轉人工客服"按鈕聯繫 @wushizhifu_jianglai。
"""
    
    def __init__(self):
        """Initialize AI service with OpenAI (priority) and Gemini (fallback)"""
        self.openai_available = False
        self.gemini_available = False
        self.openai_client = None
        self.gemini_model = None
        self.current_provider = None
        
        # Try to initialize OpenAI first (priority)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_key)
                self.openai_available = True
                self.current_provider = "openai"
                logger.info("✅ OpenAI service initialized successfully")
            except ImportError:
                logger.warning("openai package not installed, install with: pip install openai")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI service: {e}")
        
        # Try to initialize Gemini as fallback
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                # Try gemini-1.5-pro-latest first, fallback to gemini-pro if not available
                try:
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')
                except Exception:
                    # Fallback to gemini-pro for v1beta compatibility
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                self.gemini_available = True
                if not self.openai_available:
                    self.current_provider = "gemini"
                    logger.info("✅ Gemini service initialized successfully (as primary)")
                else:
                    logger.info("✅ Gemini service initialized successfully (as fallback)")
            except ImportError:
                logger.warning("google-generativeai package not installed, install with: pip install google-generativeai")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini service: {e}")
        
        if not self.openai_available and not self.gemini_available:
            logger.warning("⚠️ No AI service available. Please configure OPENAI_API_KEY or GEMINI_API_KEY")
    
    def is_available(self) -> bool:
        """Check if any AI service is available"""
        return self.openai_available or self.gemini_available
    
    def _generate_with_openai(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[str]:
        """Generate response using OpenAI"""
        if not self.openai_available or not self.openai_client:
            return None
        
        try:
            openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            # Build messages for OpenAI API
            messages = [{"role": "system", "content": self.KNOWLEDGE_BASE}]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API (new SDK format)
            response = self.openai_client.chat.completions.create(
                model=openai_model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}", exc_info=True)
            return None
    
    def _generate_with_gemini(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[str]:
        """Generate response using Gemini"""
        if not self.gemini_available or not self.gemini_model:
            return None
        
        try:
            # Build prompt with knowledge base and conversation history
            prompt = self.KNOWLEDGE_BASE + "\n\n"
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    role = "用戶" if msg.get("role") == "user" else "助手"
                    prompt += f"{role}：{msg.get('content', '')}\n"
            
            prompt += f"\n用戶問題：{user_message}\n\n請回答："
            
            # Generate response
            response = self.gemini_model.generate_content(prompt)
            answer = response.text.strip()
            logger.info(f"Gemini response generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}", exc_info=True)
            return None
    
    def generate_response(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate AI response to user message with automatic fallback.
        Priority: OpenAI -> Gemini
        
        Args:
            user_message: User's message
            conversation_history: List of previous messages [{"role": "user|assistant", "content": "..."}]
            
        Returns:
            AI generated response
        """
        if not self.is_available():
            return "抱歉，AI 服務暫時不可用，請聯繫人工客服 @wushizhifu_jianglai"
        
        answer = None
        used_provider = None
        
        # Try OpenAI first (priority)
        if self.openai_available:
            answer = self._generate_with_openai(user_message, conversation_history)
            if answer:
                used_provider = "openai"
                self.current_provider = "openai"
        
        # Fallback to Gemini if OpenAI failed or unavailable
        if not answer and self.gemini_available:
            logger.info("OpenAI failed or unavailable, falling back to Gemini")
            answer = self._generate_with_gemini(user_message, conversation_history)
            if answer:
                used_provider = "gemini"
                self.current_provider = "gemini"
        
        if not answer:
            logger.error("Both OpenAI and Gemini failed to generate response")
            return "抱歉，處理您的問題時遇到錯誤，請聯繫人工客服 @wushizhifu_jianglai"
        
        # Check if response indicates need for human support
        if self._should_escalate_to_human(answer):
            return answer + "\n\n如果以上信息無法解決您的問題，請點擊下方按鈕聯繫人工客服。"
        
        return answer
    
    def _should_escalate_to_human(self, response: str) -> bool:
        """
        Check if response indicates need for human support.
        
        Args:
            response: AI generated response
            
        Returns:
            True if should escalate to human
        """
        # Keywords that suggest need for human support
        escalation_keywords = [
            "不清楚", "不知道", "無法確定", "無法回答",
            "建議聯繫", "請聯繫客服", "無法解決",
            "需要人工", "轉人工"
        ]
        
        response_lower = response.lower()
        return any(keyword in response_lower for keyword in escalation_keywords)


# Global AI service instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get global AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
