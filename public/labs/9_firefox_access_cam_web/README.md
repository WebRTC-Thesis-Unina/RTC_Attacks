# Scenario 9: Permission abuse
- Vulnerable components: Firefox and Firefox ESR
- Affected versions:
    - for Firefox: < 69
    - for Firefox ESR: < 68.1
- CVE ID: [CVE-2019-11748](https://nvd.nist.gov/vuln/detail/CVE-2019-11748)

## Description
In this scenario, after launching the phishing campaign, the user receives the email. They decide to click the button and are redirected to the landing page managed by the attacker. On this page, they enter their data, which is captured by the attacker, and are then redirected to their intended web page. On this page, the user grants permissions to access the microphone. Believing these permissions are used for chat purposes, the user inadvertently allows the attacker to access the audio and video stream, which can then be used on third-party sites.

## How to reproduce the issue
### Step 1: Create a phising mail
To run Firefox with a graphical interface from the container, it is necessary to allow local root users to access the host display. On the host machine, execute:
```bash
sudo xhost +local:root
```
Then start firefox container with:
```bash
docker exec -it firefox bash
firefox
```
In another terminal, access the GoPhish container and start the service:
```bash
docker exec -it gophish bash
./gophish
```
Next, open ```https://127.0.0.1:3333``` in the Firefox browser.

The sender profile is defined as follows:

![sending_profile](/public/labs/9_firefox_access_cam_web/img/sending_profiles.png)

Next, the landing page is configured (that is, the page to which the user is redirected after clicking the button):

![landing_page](/public/labs/9_firefox_access_cam_web/img/landing_page.png)

The email template is defined:

![email_template](/public/labs/9_firefox_access_cam_web/img/email_template.png)

The group of users targeted by the message is specified:

![group](/public/labs/9_firefox_access_cam_web/img/users_group.png)

Finally, a campaign is created and launched:

![campaign](/public/labs/9_firefox_access_cam_web/img/campaign.png)

### Step 2: Fall into the trap
The effect is that the email is delivered to the user:

![email](/public/labs/9_firefox_access_cam_web/img/email.png)

The user clicks the button and is redirected to the landing page:

![login](/public/labs/9_firefox_access_cam_web/img/login_page.png)

By entering their credentials, the user is in fact providing them to the attacker:

![details](/public/labs/9_firefox_access_cam_web/img/details.png)

### Step 3: Exploit the vulnerability
At this point, the user is redirected to the attacker’s page, and by granting access to the microphone for what appears to be a conversation, they are effectively allowing the attacker to use these permissions on third-party pages. In the vulnerable versions, the browser retains granted permissions and applies them on third-party pages as well.

>**Note**: The user must use vulnerable versions of Firefox browser.

## Mitigation
- Update to patched version.