# tours/context_processors.py
from proposal.models import Proposal, ProposalStatus   # import the inner class

def tour_proposal_badge(request):
    if not request.user.is_authenticated:
        return {}
    if getattr(request.user, 'user_type', None) != 'tour_operator':
        return {}

    unread = request.user.received_proposals.filter(
        status__in=[ProposalStatus.SENT, ProposalStatus.COUNTERED]   # ← correct
    ).count()

    from tours.models import TourOperator
    try:
        tour_op = TourOperator.objects.get(user=request.user)
    except TourOperator.DoesNotExist:
        return {}

    return {
        'tour_operator': tour_op,
        'unread_proposal_count': unread,
        'USER_BASE': 'tours/base.html',     # ← tour-operator sees tour UI
    }