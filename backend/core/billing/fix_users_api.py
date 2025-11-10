"""
Utility API to fix users stuck with tier='none' and grant them full access.
This can be used to bulk-fix users or fix individual stuck users.
"""
from fastapi import APIRouter, Depends, HTTPException
from core.utils.auth_utils import verify_and_get_user_id_from_jwt
from core.utils.logger import logger
from core.services.supabase import DBConnection
from decimal import Decimal
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/billing", tags=["billing-fix"])

@router.post("/fix-my-account")
async def fix_my_account(
    account_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """
    Fix the current user's account by granting them full access.
    This is useful if a user got stuck with tier='none'.
    """
    try:
        logger.info(f"[FIX ACCOUNT] Fixing account for {account_id}")
        
        db = DBConnection()
        client = await db.client
        
        # Check current tier
        result = await client.from_('credit_accounts').select('tier, balance').eq('account_id', account_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        
        current_tier = result.data[0].get('tier')
        current_balance = result.data[0].get('balance', '0')
        
        logger.info(f"[FIX ACCOUNT] Current tier: {current_tier}, balance: {current_balance}")
        
        # If tier is already set and not 'none', just return success
        if current_tier and current_tier != 'none':
            return {
                'success': True,
                'message': f'Account already has tier: {current_tier}',
                'tier': current_tier,
                'balance': current_balance
            }
        
        # Grant Starter tier with credits
        default_tier = 'tier_2_20'
        new_balance = Decimal('20.00')
        next_grant = datetime.now(timezone.utc) + timedelta(days=30)
        
        await client.from_('credit_accounts').update({
            'tier': default_tier,
            'balance': str(new_balance),
            'billing_cycle_anchor': datetime.now(timezone.utc).isoformat(),
            'next_credit_grant': next_grant.isoformat(),
            'last_grant_date': datetime.now(timezone.utc).isoformat()
        }).eq('account_id', account_id).execute()
        
        logger.info(f"[FIX ACCOUNT] ✅ Granted {default_tier} tier with ${new_balance} credits to {account_id}")
        
        return {
            'success': True,
            'message': 'Account fixed! You now have full access.',
            'tier': default_tier,
            'credits_granted': str(new_balance),
            'features': {
                'monthly_credits': '$20',
                'ai_models': 'All models',
                'projects': '100',
                'threads': '100',
                'concurrent_runs': '3',
                'custom_agents': '2'
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FIX ACCOUNT] Error fixing account {account_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/fix-all-none-tier-users")
async def fix_all_none_tier_users(
    account_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """
    ADMIN ONLY: Fix all users with tier='none' by granting them full access.
    This is a bulk operation to fix all stuck users at once.
    """
    try:
        logger.info(f"[FIX ALL] Admin {account_id} initiated bulk fix for tier='none' users")
        
        db = DBConnection()
        client = await db.client
        
        # TODO: Add admin check here if you have admin roles implemented
        # For now, anyone can call this but you should restrict it
        
        # Find all users with tier='none'
        result = await client.from_('credit_accounts').select('account_id, tier').eq('tier', 'none').execute()
        
        if not result.data or len(result.data) == 0:
            return {
                'success': True,
                'message': 'No users with tier=none found',
                'fixed_count': 0
            }
        
        users_to_fix = result.data
        fixed_count = 0
        errors = []
        
        default_tier = 'tier_2_20'
        new_balance = Decimal('20.00')
        next_grant = datetime.now(timezone.utc) + timedelta(days=30)
        
        for user in users_to_fix:
            user_account_id = user['account_id']
            try:
                await client.from_('credit_accounts').update({
                    'tier': default_tier,
                    'balance': str(new_balance),
                    'billing_cycle_anchor': datetime.now(timezone.utc).isoformat(),
                    'next_credit_grant': next_grant.isoformat(),
                    'last_grant_date': datetime.now(timezone.utc).isoformat()
                }).eq('account_id', user_account_id).execute()
                
                fixed_count += 1
                logger.info(f"[FIX ALL] Fixed {user_account_id}")
                
            except Exception as e:
                error_msg = f"Failed to fix {user_account_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"[FIX ALL] {error_msg}")
        
        logger.info(f"[FIX ALL] ✅ Fixed {fixed_count} users")
        
        return {
            'success': True,
            'message': f'Fixed {fixed_count} users',
            'fixed_count': fixed_count,
            'total_found': len(users_to_fix),
            'errors': errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"[FIX ALL] Error in bulk fix: {e}")
        raise HTTPException(status_code=500, detail=str(e))

