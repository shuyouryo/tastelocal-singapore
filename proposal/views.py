# proposal/views.py
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Proposal, TransitionError, ProposalStatus
from .forms import ProposalForm, ResponseForm


@login_required
def create_proposal(request):
    initial = {}
    if 'receiver' in request.GET:
        initial['receiver'] = request.GET['receiver']
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'

    if request.method == 'POST':
        form = ProposalForm(request.POST, initial=initial)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.sender = request.user
            prop.status = ProposalStatus.DRAFT
            prop.save()
            prop.send(request)                       # ← pass request
            messages.success(request, 'Proposal sent – waiting for response.')
            return redirect('proposal:detail', pk=prop.id)
    else:
        form = ProposalForm(initial=initial)
    return render(request, 'proposal/create.html', {'form': form, 'next': next_url})


@login_required
def respond_proposal(request, pk):
    prop = get_object_or_404(Proposal, pk=pk)
    # permission check
    if request.user == prop.sender and prop.status == 'C':
        pass
    elif request.user == prop.receiver and prop.status in {'S', 'C'}:
        pass
    else:
        messages.error(request, 'Action not allowed.')
        return redirect('proposal:detail', pk=pk)

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            try:
                if action == 'accept':
                    prop.accept(request)
                    messages.success(request, 'Proposal accepted – waiting admin verification.')
                elif action == 'reject':
                    prop.reject(request)
                    messages.success(request, 'Proposal rejected.')
                elif action == 'counter':
                    prop.counter(
                        new_sender_duties=form.cleaned_data['sender_duties'],
                        new_receiver_duties=form.cleaned_data['receiver_duties'],
                        request=request
                    )
                    messages.success(request, 'Counter-proposal sent.')
            except TransitionError as e:
                messages.warning(request, str(e))
            #  ↓↓↓  ALWAYS redirect after successful POST  ↓↓↓
            return redirect('proposal:detail', pk=pk)
        # if invalid we re-render (errors now shown below)
    else:
        form = ResponseForm(initial={
            'sender_duties': prop.sender_duties,
            'receiver_duties': prop.receiver_duties,
        })

    return render(request, 'proposal/respond.html', {'proposal': prop, 'form': form})

def proposal_detail(request, pk):
    """Both parties can read current state."""
    prop = get_object_or_404(Proposal, pk=pk)
    if not (prop.is_sender(request.user) or prop.is_receiver(request.user)):
        messages.error(request, 'You are not part of this proposal.')
        return redirect('webapp:homepage')
    return render(request, 'proposal/detail.html', {'proposal': prop})

@login_required
def my_proposals(request):
    """Show every proposal this user is part of (sender or receiver)."""
    proposals = Proposal.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).order_by('-created_at')

    return render(request, 'proposal/my_proposals.html', {'proposals': proposals})

# ---------------------------------------------------------
# 1.  Re-usable helper that builds the identical sentence
# ---------------------------------------------------------
def _rejection_notice(proposal, recipient_user):
    """
    Compose the single sentence required for ANY rejection:
    'FirstName LastName, BusinessName was unable to fulfil the terms
     and has rejected your proposal offer.'
    """
    sender = proposal.sender          # TourOperator or Vendor
    fname  = sender.user.first_name
    lname  = sender.user.last_name
    biz    = getattr(sender, 'company_name', None) or getattr(sender, 'business_name', None)

    sentence = (
        f"{fname} {lname}, {biz} was unable to fulfil the terms "
        "and has rejected your proposal offer."
    )

    # 1) instant message bubble
    messages.info(recipient_user, sentence)

    # 2) (optional) persist in Notification model, e-mail, push, etc.
    # Notification.objects.create(user=recipient_user, body=sentence)


# ---------------------------------------------------------
# 2.  Thin wrappers that reject AND notify
# ---------------------------------------------------------
def _reject_original(proposal, request):
    """Reject the original proposal and notify its sender."""
    proposal.reject(request)          # your existing status-change logic
    _rejection_notice(proposal, proposal.sender.user)


def _reject_counter(counter, request):
    """
    Reject a counter-proposal and notify the party that *made* the counter.
    `counter` is expected to be a Proposal instance with status='C'
    (your counter-proposals are still rows in the same Proposal table).
    """
    counter.reject(request)           # your existing status-change logic
    _rejection_notice(counter, counter.sender.user)   # counter-proposer


# ---------------------------------------------------------
# 3.  Hook the wrappers into the respond view
# ---------------------------------------------------------
@login_required
def respond_proposal(request, pk):
    prop = get_object_or_404(Proposal, pk=pk)

    # … your existing permission block …
    if request.user == prop.sender and prop.status == 'C':
        pass
    elif request.user == prop.receiver and prop.status in {'S', 'C'}:
        pass
    else:
        messages.error(request, 'Action not allowed.')
        return redirect('proposal:detail', pk=pk)

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            try:
                if action == 'accept':
                    prop.accept(request)
                    messages.success(request, 'Proposal accepted – waiting admin verification.')

                elif action == 'reject':
                    # ORIGINAL rejection
                    if prop.status == 'S':               # receiver rejects original
                        _reject_original(prop, request)
                    else:                                # sender rejects counter
                        _reject_counter(prop, request)
                    messages.success(request, 'Proposal rejected.')

                elif action == 'counter':
                    prop.counter(
                        new_sender_duties=form.cleaned_data['sender_duties'],
                        new_receiver_duties=form.cleaned_data['receiver_duties'],
                        request=request
                    )
                    messages.success(request, 'Counter-proposal sent.')
            except TransitionError as e:
                messages.warning(request, str(e))

            return redirect('proposal:detail', pk=pk)
    # … rest of the view unchanged …