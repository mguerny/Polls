from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        ret = [Question.objects.filter(pub_date__lte=timezone.now())  # current polls
                                .filter(exp_date__gte=timezone.now())
                                .order_by('-pub_date'),
               Question.objects.filter(pub_date__lte=timezone.now())  # past polls
                                .filter(exp_date__lte=timezone.now())
                                .order_by('-exp_date')]
        return ret


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    data = []
    labels = []
    total = 0
    for choice in question.choice_set.all():
        total += choice.votes
    for choice in question.choice_set.all():
        percentage = "{:.2f}".format(choice.votes/total*100)
        data.append(choice.votes)
        labels.append(str(percentage) + "%   " + choice.choice_text + "     ")

    return render(request, 'polls/results.html', {
        'labels': labels,
        'data': data,
    })


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
