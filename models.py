from django.db import models

class BankStatement(models.Model):
    date = models.DateField()
    narration = models.CharField(max_length=255)
    amount = models.FloatField()
    type = models.CharField(max_length=20)

    def __str__(self):
        return self.narration


class InternalLedger(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.FloatField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.description


class Ledger(models.Model):
    date = models.DateField()
    amount = models.FloatField()
    category = models.CharField(max_length=100)
    source = models.CharField(max_length=50)
    reconciliation_status = models.CharField(max_length=50)

    def __str__(self):
        return self.category
        