# proposal/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ProposalStatus(models.TextChoices):
    DRAFT     = 'D', 'Draft'
    SENT      = 'S', 'Sent'
    ACCEPTED  = 'A', 'Accepted'
    REJECTED  = 'R', 'Rejected'
    COUNTERED = 'C', 'Countered'


class Proposal(models.Model):
    status = models.CharField(max_length=1, choices=ProposalStatus.choices,
                              default=ProposalStatus.DRAFT)
    sender   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_proposals')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_proposals')
    sender_duties   = models.TextField()
    receiver_duties = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---------- behaviour – now accept request ----------
    def send(self, request) -> None:                       # ← request added
        from .services import ProposalTransitionService
        ProposalTransitionService.send(self, request)      # forward request

    def accept(self, request) -> None:                     # ← request added
        from .services import ProposalTransitionService
        ProposalTransitionService.accept(self, request)

    def reject(self, request) -> None:                     # ← request added
        from .services import ProposalTransitionService
        ProposalTransitionService.reject(self, request)

    def counter(self, *, new_sender_duties: str, new_receiver_duties: str, request):
        from .services import ProposalTransitionService
        ProposalTransitionService.counter(self, new_sender_duties, new_receiver_duties, request)

    # helpers
    def is_sender(self, user):
        return self.sender_id == user.id

    def is_receiver(self, user):
        return self.receiver_id == user.id

    def __str__(self):
        return f'Proposal {self.id}  ({self.sender} → {self.receiver})  {self.get_status_display()}'


class ProposalHistory(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='history')
    sender_duties = models.TextField()
    receiver_duties = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class TransitionError(RuntimeError):
    """Raised when an illegal state transition is requested."""