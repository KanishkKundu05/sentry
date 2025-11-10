from typing import Dict, Optional
import stripe
from core.services.supabase import DBConnection
from core.utils.config import config
from core.utils.logger import logger
from .config import FREE_TIER_INITIAL_CREDITS

class FreeTierService:
    def __init__(self):
        self.stripe = stripe
        
    async def auto_subscribe_to_free_tier(self, account_id: str, email: Optional[str] = None) -> Dict:
        """
        Give all new users full access without requiring Stripe subscription.
        Sets tier to 'tier_2_20' (Starter) with generous credits and limits.
        """
        db = DBConnection()
        client = await db.client
        
        try:
            logger.info(f"[FREE TIER] Auto-subscribing user {account_id} to full access tier")
            
            # Check if user already has a tier set
            existing = await client.from_('credit_accounts').select(
                'tier'
            ).eq('account_id', account_id).execute()
            
            if existing.data and len(existing.data) > 0:
                current_tier = existing.data[0].get('tier', 'none')
                if current_tier != 'none':
                    logger.info(f"[FREE TIER] User {account_id} already has tier {current_tier}, skipping")
                    return {'success': True, 'message': 'Already has tier', 'tier': current_tier}
            
            # Give everyone Starter tier (tier_2_20) by default with full access
            # This tier includes:
            # - $20 monthly credits
            # - All AI models access
            # - 100 projects/threads
            # - 3 concurrent runs
            # - 2 custom agents
            default_tier = 'tier_2_20'
            
            from decimal import Decimal
            from datetime import datetime, timezone, timedelta
            
            # Grant initial credits
            next_grant = datetime.now(timezone.utc) + timedelta(days=30)
            
            await client.from_('credit_accounts').update({
                'tier': default_tier,
                'balance': str(Decimal('20.00')),  # Give $20 credits immediately
                'billing_cycle_anchor': datetime.now(timezone.utc).isoformat(),
                'next_credit_grant': next_grant.isoformat(),
                'last_grant_date': datetime.now(timezone.utc).isoformat()
            }).eq('account_id', account_id).execute()
            
            logger.info(f"[FREE TIER] ✅ Granted {default_tier} tier with $20 credits to {account_id}")
            
            return {
                'success': True,
                'tier': default_tier,
                'message': 'Full access granted'
            }
            
        except Exception as e:
            logger.error(f"[FREE TIER] Error auto-subscribing {account_id}: {e}")
            return {'success': False, 'error': str(e)}

free_tier_service = FreeTierService()

