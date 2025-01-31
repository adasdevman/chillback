from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from payments.models import Payment # type: ignore

@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by('-created_at')
    return render(request, 'dashboard/payments/list.html', {'payments': payments})

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'dashboard/payments/detail.html', {'payment': payment})

@login_required
def payment_edit(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment.status = request.POST.get('status')
        payment.amount = request.POST.get('amount')
        payment.payment_type = request.POST.get('payment_type')
        payment.description = request.POST.get('description')
        payment.save()
        
        messages.success(request, 'Paiement mis à jour avec succès.')
        return redirect('dashboard:payment_detail', payment_id=payment.id)
    
    return render(request, 'dashboard/payments/edit.html', {'payment': payment})

@login_required
def payment_delete(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Paiement supprimé avec succès.')
        return redirect('dashboard:payments')
    
    return redirect('dashboard:payment_detail', payment_id=payment.id) 