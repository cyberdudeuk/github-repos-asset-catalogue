# Sharing actions and workflows with your organization

You can share an action or reusable workflow with your organization without publishing the action or workflow publicly.

> \[!WARNING]
>
> * If you make a private repository accessible to GitHub Actions workflows in other repositories, outside collaborators on the other repositories can indirectly access the private repository, even though they do not have direct access to these repositories. The outside collaborators can view logs for workflow runs when actions or workflows from the private repository are used.
> * To allow runners to download these actions, GitHub passes a scoped installation token to the runner. This token has read access to the repository, and automatically expires after one hour.

## Sharing actions and workflows with your organization

1. Store the action or reusable workflow in a private repository. For more information, see [About repositories](/en/repositories/creating-and-managing-repositories/about-repositories#about-repository-visibility).
2. On GitHub, navigate to the main page of the private repository.
3. Under your repository name, click ** Settings**.
4. In the left sidebar, click ** Actions**, then click **General**.
5. To grant access to other private repositories in the organization, in the **Access** section at the bottom of the page, select **Accessible from repositories in the 'ORGANIZATION-NAME' organization**.
6. Click **Save** to apply the settings.

## Next steps

To learn how to reuse your shared workflows, see [Reuse workflows](/en/actions/how-tos/reuse-automations/reuse-workflows).