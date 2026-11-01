# Verifying your custom domain for GitHub Pages

You can increase the security of your custom domain and avoid takeover attacks by verifying your domain.

## About domain verification for GitHub Pages

When you verify a custom domain for your personal account, only repositories owned by your personal account may be used to publish a GitHub Pages site to the verified custom domain or the domain's immediate subdomains. Similarly, when you verify a custom domain for your organization, only repositories owned by that organization may be used to publish a GitHub Pages site to the verified custom domain or the domain's immediate subdomains.

Verifying your domain stops other GitHub users from taking over your custom domain and using it to publish their own GitHub Pages site. Domain takeovers can happen when you delete your repository, when your billing plan is downgraded, or after any other change which unlinks the custom domain or disables GitHub Pages while the domain remains configured for GitHub Pages and is not verified.

When you verify a domain, any immediate subdomains are also included in the verification. For example, if the `github.com` custom domain is verified, `docs.github.com`, `support.github.com`, and any other immediate subdomains will also be protected from takeovers.<!-- markdownlint-disable-line search-replace -->

> \[!WARNING]
> We strongly recommend that you do not use wildcard DNS records, such as `*.example.com`. These records put you at an immediate risk of domain takeovers, even if you verify the domain. For example, if you verify `example.com` this prevents someone from using `a.example.com` but they could still take over `b.a.example.com` (which is covered by the wildcard DNS record).

It's also possible to verify a domain for your organization, which displays a "Verified" badge on the organization  profile. For more information, see [Verifying or approving a domain for your organization](/en/organizations/managing-organization-settings/verifying-or-approving-a-domain-for-your-organization).

### Verifying a domain that is already taken

You may be verifying a domain you own, which is currently in use by another user or organization, to make it available for your GitHub Pages website. In this case, the domain will be immediately released from GitHub Pages websites which are owned by other users or organizations. If you are attempting to verify an already verified domain (verified by another user or organization), the release process will not be successful.

## Verifying a domain for your user site

> \[!NOTE]
> If you don’t see the options described below, make sure you’re in your **Profile settings**, not your repository settings. Domain verification happens at the profile level.

1. In the upper-right corner of any page on GitHub, click your profile picture, then click ** Settings**.

2. In the sidebar, under "Code, planning, and automation", click ** Pages**.

3. On the right, click **Add a domain**.

4. Under "What domain would you like to add?," enter the domain you wish to verify and select **Add domain**.
   ![Screenshot of the field to add a verified domain for your GitHub Pages site. A green "Add domain" button is shown below the field.](/assets/images/help/pages/verify-enter-domain.png)

5. Follow the instructions under "Add a DNS TXT record" to create the TXT record with your domain hosting service.
   ![Screenshot of GitHub Pages instructions to add a TXT record to the DNS configuration of example.com.](/assets/images/help/pages/verify-dns.png)

6. Wait for your DNS configuration to change, this may be immediate or take up to 24 hours. You can confirm the change to your DNS configuration by running the `dig` command on the command line. In the command below, replace `USERNAME` with your username and `example.com` with the domain you're verifying. If your DNS configuration has updated, you should see your new TXT record in the output.

   ```text
   dig _github-pages-challenge-USERNAME.example.com +nostats +nocomments +nocmd TXT
   ```

7. After confirming that your DNS configuration has updated, you can verify the domain. If the change wasn't immediate, and you have navigated away from the previous page, return to your Pages settings by following the first few steps and, to the right of the domain, click  and then click **Continue verifying**.

   ![Screenshot of "Verified domains" settings. Under the horizontal kebab icon to the right, the "Continue verifying" option is outlined in orange.](/assets/images/help/pages/verify-continue.png)

8. To verify your domain, click **Verify**.

9. To make sure your custom domain remains verified, keep the TXT record in your domain's DNS configuration.

## Verifying a domain for your organization site

Organization owners can verify custom domains for their organization.

> \[!NOTE]
> If you don’t see the options described below, check that you’re in your **Organization settings**. Domain verification doesn’t take place in repository settings.

1. In the upper-right corner of GitHub, click your profile picture, then click ** Organizations**.

2. Select an organization by clicking on it.

3. Under your organization name, click **** dropdown menu, then click **Settings**.

   ![Screenshot of the tabs in an organization's profile. The "Settings" tab is outlined in dark orange.](/assets/images/help/discussions/org-settings-global-nav-update.png)

4. In the sidebar, under "Code, planning, and automation", click ** Pages**.

5. On the right, click **Add a domain**.

6. Under "What domain would you like to add?," enter the domain you wish to verify and select **Add domain**.
   ![Screenshot of the field to add a verified domain for your GitHub Pages site. A green "Add domain" button is shown below the field.](/assets/images/help/pages/verify-enter-domain.png)

7. Follow the instructions under "Add a DNS TXT record" to create the TXT record with your domain hosting service.
   ![Screenshot of GitHub Pages instructions to add a TXT record to the DNS configuration of example.com.](/assets/images/help/pages/verify-dns.png)

8. Wait for your DNS configuration to change. This may be immediate or take up to 24 hours. You can confirm the change to your DNS configuration by running the `dig` command on the command line. In the command below, replace `ORGANIZATION` with the name of your organization and `example.com` with the domain you're verifying. If your DNS configuration has updated, you should see your new TXT record in the output.

   ```text
   dig _github-pages-challenge-ORGANIZATION.example.com +nostats +nocomments +nocmd TXT
   ```

9. After confirming that your DNS configuration has updated, you can verify the domain. If the change wasn't immediate, and you have navigated away from the previous page, return to your Pages settings by following the first few steps and, to the right of the domain, click  and then click **Continue verifying**.

   ![Screenshot of "Verified domains" settings. Under the horizontal kebab icon to the right, the "Continue verifying" option is outlined in orange.](/assets/images/help/pages/verify-continue.png)

10. To verify your domain, click **Verify**.

11. To make sure your custom domain remains verified, keep the TXT record in your domain's DNS configuration.