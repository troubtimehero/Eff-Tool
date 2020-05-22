from django.db import models


class Words20000(models.Model):
    word = models.CharField(max_length=32)

    class Meta:
        db_table = 'words20000'

    @staticmethod
    def create(w):
        model = Words20000()
        model.word = w
        return model
