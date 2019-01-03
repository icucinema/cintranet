import uuid
import random
import os.path

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

def paste_determine_filename(instance, filename):
    if '.' in filename:
        filename, _, ext = filename.rpartition('.')
    else:
        ext = 'bin'
    return os.path.join('cinbin_images', uuid.uuid4().hex + '.' + ext)


def slug_generator():
    ADJECTIVES = ['tasty', 'delicious', 'scrummy', 'yummy', 'appetizing', 'disgusting', 'gross', 'hideous', 'beautiful', 'fluorescent', 'friendly', 'evil', 'good', 'nice', 'riveting', 'indigestible', 'foreign', 'violent', 'gentle', 'peaceful', 'shiny', 'dull', 'exciting', 'boring', 'fun']
    COLOURS = ['orange', 'blue', 'silver', 'gold', 'yellow', 'red', 'bronze', 'indigo', 'black', 'white', 'green', 'turquoise', 'brown', 'violet', 'cyan', 'magenta']
    NOUNS = ['chocolate', 'toffee', 'coffee', 'salad', 'bacon', 'caramel', 'pineapple', 'bacon', 'fish', 'salmon', 'toast', 'tea', 'milk', 'sandwich', 'rice', 'potato', 'soup', 'tomato']
    slug = [random.choice(ADJECTIVES), random.choice(COLOURS), random.choice(NOUNS)]
    return '-'.join(slug)

class BasePaste(models.Model):
    slug = models.CharField(max_length=256, default='', null=False, unique=True)
    user = models.ForeignKey(User, models.CASCADE)
    public = models.BooleanField(default=False, blank=False, null=False)
    posted = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        setting_slug = False
        if force_insert or self.slug is None or len(self.slug) == 0:
            setting_slug = True
            self.slug = uuid.uuid1().hex

        super(BasePaste, self).save(force_insert=force_insert, force_update=force_update, *args, **kwargs)

        if setting_slug:
            self.slug = '{}-{}'.format(self.pk, slug_generator())
            self.save()

    class Meta:
        abstract = True

class TextPaste(BasePaste):
    content = models.TextField(null=False, blank=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cinbin:cinbin_textpaste', kwargs={'slug': self.slug})

class ImagePaste(BasePaste):
    content = models.ImageField(upload_to=paste_determine_filename)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cinbin:cinbin_imagepaste', kwargs={'slug': self.slug})