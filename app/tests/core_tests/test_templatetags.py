import pytest
from django.template import Context, RequestContext, Template
from django.test import RequestFactory, override_settings

from tests.factories import ChallengeFactory, PageFactory


@pytest.mark.django_db
def test_taglist():
    template = Template(
        "{% load taglist from grandchallenge_tags %}{% taglist %}"
    )
    rendered = template.render(Context({}))
    assert "<td>listdir</td>" in rendered


@pytest.mark.django_db
def test_url_parameter(rf: RequestFactory):
    r = rf.get("/who?me=john")
    template = Template(
        "{% load url_parameter from grandchallenge_tags %}"
        "{% url_parameter me %}"
    )
    context = RequestContext(request=r)
    rendered = template.render(context)
    assert rendered == "john"


@pytest.mark.django_db
@pytest.mark.parametrize("view_type", ["anode09", "anode09_table"])
@override_settings(MEDIA_ROOT="/app/tests/core_tests/resources/")
def test_insert_graph(rf: RequestFactory, view_type):
    c = ChallengeFactory(short_name="testproj1734621")
    p = PageFactory(challenge=c)
    r = rf.get("/Result/?id=4")
    template = Template(
        "{% load insert_graph from grandchallenge_tags %}"
        "{% insert_graph 4.php type:"
        f"{view_type}"
        " %}"
    )
    context = RequestContext(r, {"currentpage": p})
    rendered = template.render(context)
    assert "pageError" not in rendered
    assert "Error rendering graph from file" not in rendered
    if view_type == "anode09":
        assert "Created with matplotlib" in rendered
    else:
        assert "tablecontainer" in rendered


@pytest.mark.django_db
def test_google_group():
    template = Template(
        "{% load google_group from grandchallenge_tags %}{% google_group 'my-group' %}"
    )
    rendered = template.render(Context({}))
    assert 'data-groupname="my-group"' in rendered
