# proposal/infrastructure.py
from django.contrib import messages


class InAppMessager:
    """ Thin adapter – can be replaced with SMS / e-mail later. """

    @staticmethod
    def new_proposal(prop, request):               # ← request param added
        msg = f'New proposal #{prop.id} from {prop.sender.get_full_name() or prop.sender.email}'
        messages.info(request, msg)                # ← request first

    @staticmethod
    def rejected(prop, request):                   # ← request param added
        txt = f'Proposal #{prop.id} has been rejected.'
        messages.warning(request, txt)             # ← request first

    @staticmethod
    def accepted(prop, request):                   # ← request param added
        txt = f'Proposal #{prop.id} accepted – waiting for admin verification.'
        messages.success(request, txt)             # ← request first

    @staticmethod
    def countered(prop, request):                  # ← request param added
        if prop.is_sender(prop.receiver):   # receiver just countered
            messages.info(request, f'Proposal #{prop.id} countered – please review')
        else:
            messages.info(request, f'Proposal #{prop.id} countered – please review')


class AdminNotifier:
    @staticmethod
    def new_agreement(prop):
        print(f'[ADMIN-QUEUE] Proposal {prop.id} ready for manual verification')