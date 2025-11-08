{% comment %} Dynamic version detection using projects.json {% endcomment %}
{% assign kaniop_project = site.data.projects | where: 'project', 'kaniop' | first %}
{% assign currentVersion = page.currentVersion | default: 'latest' %}
{% assign currentPath = page.currentPath | default: '/' %}

{% comment %} Set version-aware URLs {% endcomment %}
{% assign currentDocsPath = '/docs/kaniop/' | append: currentVersion | append: '/' %}
{% assign latestDocsPath = '/docs/kaniop/latest/' %}

{% comment %} Main navigation links {% endcomment %}
{% assign blogLink = 'https://github.com/pando85/kaniop/discussions' %}
{% assign communityMeetingLink = 'https://github.com/pando85/kaniop/discussions' %}
{% assign contributeLink = 'https://github.com/pando85/kaniop/blob/master/CONTRIBUTING.md' %}
{% assign discussionLink = 'https://github.com/pando85/kaniop/discussions' %}
{% assign featureRequestLink = 'https://github.com/pando85/kaniop/issues' %}
{% assign newIssueLink = 'https://github.com/pando85/kaniop/issues/new' %}
{% assign gettingStartedLink = currentDocsPath | append: 'getting-started.html' %}
{% assign githubLink = 'https://github.com/pando85/kaniop' %}
{% assign apiGithubLink = 'https://api.github.com/repos/pando85/kaniop' %}
{% assign latestDocs = latestDocsPath %}
{% assign currentDocs = currentDocsPath %}
{% assign releasesLink = 'https://github.com/pando85/kaniop/releases' %}
{% assign kanidmLink = 'https://kanidm.com' %}

{% comment %} Legacy aliases for compatibility {% endcomment %}
{% assign communityLink = discussionLink %}
{% assign issueLink = featureRequestLink %}
{% assign docsLink = latestDocs %}
