![glide logo](glide-logo.png)
# Glide

## What is it?

Glide is a management tool for frontend apps which allows you to perform virtually any operations you would through your hosting service.
Glide can seamlessly integrate with the following cloud services:
- AWS S3
- Netlify
- Vercel
- Digital Ocean
- Azure

Since Glide is in beta, it does not yet support all of the above cloud services.

Glide enables you to migrate your applications from one cloud service to another with just one cli command.

## Usage

```
$ glide

Usage: glide [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  deploy  Deploys a directory to given cloud provider.
  init    Creates a basic glide config file.
  sites   Shows all available user sites.
```

## Install

For now in order to install Glide on your system, you need to build it from source. Thankfully that is super easy. All you need is Python and prefferably, a virtualenv.

Clone the repo on your system and run `python3 -m pip install --editable .` in order to install the Glide CLI locally.

## Why?

Think about this, you have just created a big frontend application in react which uses Netlify serverless functions. Now you face some problem with Netlify as your cloud service provider. How would you migrate your entire frontend infrastructure? Enter Glide. With Glide you would only need to manage one configuration file and everything else will be managed by Glide.

## Analytics

Using Glide, you can see analytics for you frontend applications, moreover, you will be able to access user/team analytics as well.

## Webhooks

Glide supports hooks but only for Netlify right now. If you do migrate to Netlify, then you would be able to set and remove hooks from the cli itself.

## Versioning

Glide also versions your deployments if the versioning field is set to true in the glide file. Glide versions all deployments made by you or your team throughout all cloud providers. 

## Notes

For AWS the region and access secret is neccessary.

Serverless is not yet supported.

## Authors

- Antariksh Verma (@yummyweb)