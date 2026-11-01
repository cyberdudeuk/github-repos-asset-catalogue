# Archiving repositories

You can archive a repository to make it read-only for all users and indicate that it's no longer actively maintained. You can also unarchive repositories that have been archived.

## About repository archival

> \[!NOTE]
> If you have a legacy per-repository billing plan, you will still be charged for your archived repository. If you don't want to be charged for an archived repository, you must upgrade to a new product. For more information, see [GitHub's plans](/en/get-started/learning-about-github/githubs-plans).

> \[!NOTE]
> Customers who use GitHub Secret Protection can enable secret scanning on archived repositories. For more information, see [Secret scanning](/en/code-security/concepts/secret-security/secret-scanning).

We recommend that you close all issues and pull requests, as well as update the README file and description, before you archive a repository.

Once a repository is archived, you cannot add or remove collaborators or teams. Contributors with access to the repository can only fork or star your project.

When a repository is archived, its issues, pull requests, code, labels, milestones, projects, wiki, releases, commits, tags, branches, reactions, code scanning alerts, comments and permissions become read-only. To make changes in an archived repository, you must unarchive the repository first.

You can search for archived repositories. For more information, see [Searching for repositories](/en/search-github/searching-on-github/searching-for-repositories#search-based-on-whether-a-repository-is-archived). You can also search for issues and pull requests within archived repositories. For more information, see [Searching issues and pull requests](/en/search-github/searching-on-github/searching-issues-and-pull-requests#search-based-on-whether-a-repository-is-archived).

To archive all repositories in an organization at once, you can archive the entire organization. For more information, see [Archiving an organization](/en/organizations/managing-organization-settings/archiving-an-organization).

## Archiving a repository

We recommend that you close all issues and pull requests, as well as update the README file and description, before you archive a repository.

1. On GitHub, navigate to the main page of the repository.
2. Under your repository name, click **** dropdown menu, then click **Settings**.

   ![Screenshot of a repository header showing the tabs. The "Settings" tab is highlighted by a dark orange outline.](/assets/images/help/repository/repo-actions-settings.png)
3. Under "Danger Zone", click **Archive this repository**
4. Read the warnings.
5. In the text field, type the name of the repository you want to archive.
   ![Screenshot showing the "Archive repository" dialog box.](/assets/images/help/repository/archive-repository-warnings.png)
6. Click **I understand the consequences, archive this repository**.

## Unarchiving a repository

1. On GitHub, navigate to the main page of the repository.
2. Under your repository name, click **** dropdown menu, then click **Settings**.

   ![Screenshot of a repository header showing the tabs. The "Settings" tab is highlighted by a dark orange outline.](/assets/images/help/repository/repo-actions-settings.png)
3. In the "Danger Zone" section, click **Unarchive this repository**
4. Read the warnings.
5. In the text box, type the name of the repository you want to unarchive.
6. Click **I understand the consequences, unarchive this repository**.