# Scenario 9: Permission abuse
### Description
In this scenario, after launching the phishing campaign, the user receives the email. They decide to click the button and are redirected to the landing page managed by the attacker. On this page, they enter their data, which is captured by the attacker, and are then redirected to their intended web page. On this page, the user grants permissions to access the microphone and camera. Believing these permissions are used for chat purposes, the user inadvertently allows the attacker to access the audio and video stream, which can then be used on third-party sites.

### How to reproduce the issue
Before starting containers, install the dependencies for the NodeJS server using:
```bash
npm i express https ws fs path
```
Then start the containers with:
```bash
docker compose up -d --build
```
The GoPhish framework is used to create a phishing campaign. First, the sender profile is defined:

![sending_profile](/9_firefox_access_cam_web/img/sending_profiles.png)

Next, the landing page is configured (that is, the page to which the user is redirected after clicking the button):

![landing_page](/9_firefox_access_cam_web/img/landing_page.png)

The email template is defined:

![email_template](/9_firefox_access_cam_web/img/email_template.png)

The group of users targeted by the message is specified:

![group](/9_firefox_access_cam_web/img/users_group.png)

Finally, a campaign is created and launched:

![campaign](/9_firefox_access_cam_web/img/campaign.png)

The effect is that the email is delivered to the user:

![email](/9_firefox_access_cam_web/img/email.png)

The user clicks the button and is redirected to the landing page:

![login](/9_firefox_access_cam_web/img/login_page.png)

By entering their credentials, the user is in fact providing them to the attacker:

![details](/9_firefox_access_cam_web/img/details.png)

At this point, the user is redirected to the attacker’s page, and by granting access to the webcam and microphone for what appears to be a conversation, they are effectively allowing the attacker to use these permissions on third-party pages.