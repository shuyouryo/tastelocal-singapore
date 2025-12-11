# proposal/services.py
from django.utils import timezone
from .models import Proposal, ProposalHistory, ProposalStatus, TransitionError
from .infrastructure import InAppMessager, AdminNotifier


class ProposalTransitionService:
    """ Stateless orchestrator – keeps models thin. """

    @staticmethod
    def send(prop, request):
        if prop.status != ProposalStatus.DRAFT:
            raise TransitionError('Only drafts can be sent')
        prop.status = ProposalStatus.SENT
        prop.save(update_fields=['status', 'updated_at'])
        InAppMessager.new_proposal(prop, request)

    @staticmethod
    def reject(prop, request):
        if prop.status not in {ProposalStatus.SENT, ProposalStatus.COUNTERED}:
            raise TransitionError('Can only reject sent / countered proposals')
        prop.status = ProposalStatus.REJECTED
        prop.save(update_fields=['status', 'updated_at'])
        InAppMessager.rejected(prop, request)

    @staticmethod
    def accept(prop, request):
        if prop.status not in {ProposalStatus.SENT, ProposalStatus.COUNTERED}:
            raise TransitionError('Can only accept sent / countered proposals')
        prop.status = ProposalStatus.ACCEPTED
        prop.save(update_fields=['status', 'updated_at'])
        InAppMessager.accepted(prop, request)
        AdminNotifier.new_agreement(prop)

    @staticmethod
    def counter(prop, *, new_sender_duties: str, new_receiver_duties: str, request):
        #  ↑↑↑  keyword-only + request last  ↑↑↑
        if prop.status not in {ProposalStatus.SENT, ProposalStatus.COUNTERED}:
            raise TransitionError('Can only counter sent / countered proposals')
        ProposalHistory.objects.create(
            proposal=prop,
            sender_duties=prop.sender_duties,
            receiver_duties=prop.receiver_duties,
        )
        prop.sender_duties   = new_sender_duties
        prop.receiver_duties = new_receiver_duties
        prop.status          = ProposalStatus.COUNTERED
        prop.save()
        InAppMessager.countered(prop, request)