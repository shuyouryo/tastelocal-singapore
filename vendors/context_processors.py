# vendors/context_processors.py
from proposal.models import Proposal, ProposalStatus   # import inner class

def vendor_proposal_badge(request):
    if not request.user.is_authenticated:
        return {}
    if getattr(request.user, 'user_type', None) != 'vendor':
        return {}

    # count proposals sent TO this user (the vendor)
    unread = request.user.received_proposals.filter(
        status__in=[ProposalStatus.SENT, ProposalStatus.COUNTERED]
    ).count()

    from vendors.models import Vendor
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        return {}

    return {
        'vendor': vendor,
        'unread_proposal_count': unread,
        'USER_BASE': 'vendors/base.html',   # ← vendor user sees vendor UI
    }
