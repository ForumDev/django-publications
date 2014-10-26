from django.db import models
from django.dispatch import receiver
from django.forms import model_to_dict
from django.template import Template, Context

class StyleTemplate(models.Model):
    style = models.ForeignKey('Style')
    bibtype = models.ForeignKey('Type')
    template = models.TextField()

    def __unicode__(self):
        return self.bibtype.type

    def format(self, publication):
        context = model_to_dict(publication)
        context['authors'] = self.format_authors(publication)

        t = self.template
        if context.get('url'):
            t = '<a href="{{ url }}">' + t + '</a>'

        t = Template(t)
        c = Context(context)
        return t.render(c)

    def format_authors(self, publication):
        names = publication.authors_list
        lnames = len(names)
        if lnames >= 4:
            return '{} et al.'.format(names[0])
        if lnames > 1:
            return '{} and {}'.format(', '.join(names[:-1]), names[-1])
        return names[0]

class Style(models.Model):
    """
    When Style created, need to create x StyleTemplate with FK to Type and FK to Style.
    When Type created, need to create new StyleTemplate for each Style.
    StyleTemplate should not ever be created manually.

    """
    name  = models.CharField(max_length=256, unique=True)
    bibtype = models.ManyToManyField('Type', through='StyleTemplate')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        from publications.models import Type
        create_style_templates = self.pk is None
        super(Style, self).save(*args, **kwargs)
        if create_style_templates:
            # Look up Types and create a StyleTemplate for each
            types = Type.objects.all()
            for t in types:
                StyleTemplate(
                        style=self,
                        bibtype=t,
                        template="",
                ).save()

@receiver(models.signals.post_save, sender='publications.Type')
def post_save_type(sender, instance, created, raw, **kwargs):
    # If loading models from a fixture, ignore because the db will get messed up
    # Similarly, if the type has already been created we don't need to do this
    if raw or not created: return
    print 'here, abort'

    # For each existing style, create a corresponding StyleTemplate to this Type
    styles = Style.objects.all()
    for s in styles:
        StyleTemplate(
                style=s,
                bibtype=instance,
                template="",
        ).save()
