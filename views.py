from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import BankStatement, InternalLedger, Ledger

@api_view(['GET'])
def run_reconciliation(request):
    # Purana data delete kar rahe hain taaki duplicate na ho
    Ledger.objects.all().delete()
    
    bank_entries = BankStatement.objects.all()
    internal_entries = InternalLedger.objects.all()
    matched_internal_ids = set()

    for bank in bank_entries:
        # Rule: Amount match + Date gap <= 2 days
        match = internal_entries.filter(
            amount=bank.amount,
            date__range=[bank.date - timedelta(days=2), bank.date + timedelta(days=2)]
        ).first()

        if match:
            status, cat, matched_id = "Matched", match.category, match.id
            matched_internal_ids.add(matched_id)
        else:
            status, cat = "Unmatched", "Unknown"

        Ledger.objects.create(
            date=bank.date,
            amount=bank.amount,
            category=cat,
            source="Bank",
            reconciliation_status=status
        )
    
    # Jo Internal entries bach gayi unhe add karna
    unmatched_internal = internal_entries.exclude(id__in=matched_internal_ids)
    for internal in unmatched_internal:
        Ledger.objects.create(
            date=internal.date,
            amount=internal.amount,
            category=internal.category,
            source="Internal",
            reconciliation_status="Unmatched"
        )
    
    return Response({"message": "Reconciliation completed successfully!"})

@api_view(['GET'])
def summary(request):
    # Task 4: Summary API
    total_credits = BankStatement.objects.filter(type='credit').aggregate(Sum('amount'))['amount__sum'] or 0
    total_debits = BankStatement.objects.filter(type='debit').aggregate(Sum('amount'))['amount__sum'] or 0
    unmatched_count = Ledger.objects.filter(reconciliation_status='Unmatched').count()
    
    return Response({
        "total_credits": total_credits,
        "total_debits": total_debits,
        "unmatched_transactions": unmatched_count
    })

@api_view(['GET'])
def category_breakdown(request):
    # Task 4: Expenses by category
    data = Ledger.objects.values('category').annotate(total_amount=Sum('amount'))
    return Response(list(data))