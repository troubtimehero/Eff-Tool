from django.db import models


class WordMeans(models.Model):
    word = models.CharField(max_length=32, unique=True)
    means = models.CharField(max_length=256)

    class Meta:
        db_table = 'translate_en_2_cn'

    @staticmethod
    def create(w, m):
        wm = WordMeans()
        wm.word = w
        wm.means = m
        return wm

