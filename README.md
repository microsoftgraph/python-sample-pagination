# Working with paginated Graph responses in Python

Some Microsoft Graph queries can return a large number of entities, more than can practically be included in a single JSON payload. In those cases, Graph _paginates_ responses to improve performance as well as developer convenience and flexibility.

This repo contains Python-based examples of how to work with Graph's paginated responses. For a high-level overview of how pagination works in Microsoft Graph, see [Paging Microsoft Graph data in your app](https://developer.microsoft.com/en-us/graph/docs/concepts/paging).

The samples in this repo use [messages](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/user_list_messages) to illustrate how pagination works, but the same concepts can be applied to any Graph API that uses pagination, including messages, [contacts](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/user_list_contacts), [users](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/user_list), [groups](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/group_list), and others.

* [Installation](#installation)
* [Basic concepts](#basic-concepts)
* [Using generators](#using-generators)
* [Contributing](#contributing)
* [Resources](#resources)

## Installation

Before installing the samples, verify that you have these prerequisites in place:

* Install Python from [https://www.python.org/](https://www.python.org/). We've tested the code with Python 3.6.2, but any Python 3.x version should work fine. If your code base is running under Python 2.7, you may find it helpful to use the [3to2](https://pypi.python.org/pypi/3to2) tools to port the code to Python 2.7.
* To register your application for access to Microsoft Graph, you'll need either a [Microsoft account](https://www.outlook.com) or an [Office 365 for business account](https://msdn.microsoft.com/en-us/office/office365/howto/setup-development-environment#bk_Office365Account). If you don't have one of these, you can create a Microsoft account for free at [outlook.com](https://www.outlook.com).

Then follow these steps to install the sample code:

1. Clone this repo: ```git clone https://github.com/microsoftgraph/python-sample-pagination.git```.
2. Create and activate a virtual environment (optional). If you're new to Python virtual environments, [Miniconda](https://conda.io/miniconda.html) is a great place to start.
3. In the root folder of your cloned repo, install the dependencies for the sample as listed in [requirements.txt](https://github.com/microsoftgraph/python-sample-pagination/blob/master/requirements.txt) with this command: ```pip install -r requirements.txt```.

To complete the configuration of the samples, you'll need to register a new application in the Microsoft Application Registration Portal. You only need to do this once, and then any Microsoft identity can be used to run the samples.

Follow these steps to register a new application:

1. Sign in to the [Application Registration Portal](https://apps.dev.microsoft.com/) using either your personal or work or school account.

2. Under **My applications**, choose **Add an app**. If you're using an Office 365 account and see two categories listed (Converged or Azure AD only), choose **Add an app** for the Converged applications section.

3. Enter an application name, and choose **Create**. (Do *not* choose **Guided Setup**.)

4. Next you'll see the registration page for your app. Copy and save the **Application Id** field.You will need it later to complete the configuration process.

5. Under **Application Secrets**, choose **Generate New Password**. A new password will be displayed in the **New password generated** dialog. Copy this password. You will need it later to complete the configuration process.

6. Under **Platforms**, choose **Add platform** > **Web**.

7. Under **Delegated Permissions**, add the **Mail.Read** permission.

8. Enter `http://localhost:5000/login/authorized` as the Redirect URL, and then choose **Save**.

As the final step in configuring the sample, modify the [config.py](https://github.com/microsoftgraph/python-sample-pagination/blob/master/config.py) file in the root folder of your cloned repo, and follow the instructions to enter your Client ID and Client Secret (which are referred to as Application Id and Password in the app registration portal). Then save the change, and you're ready to run the samples.

## Basic concepts

Graph's approach to pagination for potentially large result sets uses the [odata.context](http://docs.oasis-open.org/odata/odata-json-format/v4.0/cs01/odata-json-format-v4.0-cs01.html#_Toc365464685) and [odata.nextLink](http://docs.oasis-open.org/odata/odata-json-format/v4.0/cs01/odata-json-format-v4.0-cs01.html#_Toc365464689) annotations that are defined in [OData JSON Format Version 4.0](http://docs.oasis-open.org/odata/odata-json-format/v4.0/cs01/odata-json-format-v4.0-cs01.html).

When you query a paginated Graph API (for example, ```me/messages```), you'll get back a JSON payload that contains these top-level elements:

* ```@odata.context``` contains a URI that identifies the type of data being returned. This value is the same for every page of the result set.
* ```@odata.nextLink``` contains a link to the next page of results. You can do a GET against that endpoint to return the next page, which will contain a link to the next page after that, and you can repeat this process until the final page, which will not have this element.
* ```value``` contains the returned data, as a list of JSON elements. In the ```me/messages``` example, this would be a list of email messages. The number of items returned is based on the page size. Each paginated API has a default page size (for example, the ```me/messages``` default is 10 messages), and you can specify a different page size if desired through use of the ```$top``` parameter. Note that the default page size and maximum page size may vary for different Graph APIs &mdash; see [Paging Microsoft Graph data in your app](https://developer.microsoft.com/en-us/graph/docs/concepts/paging) for more information.

The following diagram shows how this works in practice, using the ```me/messages``` endpoint as an example.

![pagination example](static/images/pagination-example.png)

The [pagination.py](https://github.com/microsoftgraph/python-sample-pagination/blob/master/pagination.py) sample in this repo provides an interactive demonstration of how it works. Follow the [Installation](#installation) instructions to install the sample, and then run it as follows:

1. At the command prompt: ```python pagination.py```
2. Navigate a browser to [http://localhost:5000](http://localhost:5000)
3. Choose **Connect** and authenticate with a Microsoft identity (organization account or Microsoft Account)

You'll then see the following page listing your most recent 10 messages:

![most recent 10 messages](static/images/pagination-sample.png)

The ```@odata.nextLink``` value links to the next page of results. Each time you click on the **Next Page** button, the next page of results is loaded. This is the fundamental behavior of paginated responses from Graph APIs.

### What if @odata.nextLink is missing?

In some cases, Graph APIs return all of the requested entities in a single response, and in that case the `@odata.nextLink` element is missing from the response. This may also occur when you have received the last page of data. The absence of this property tells you that there are no more pages of data available in the collection.

For example, if there are less than 250 items in your OneDrive root folder, you will see this JSON response when you request all of the [DriveItems](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/resources/driveitem) in the folder by doing a GET to the ```https://graph.microsoft.com/v1.0/me/drive/root/children``` endpoint:

![root drive children](static/images/root-drive-children.png)

Since there is no ```@odata.nextLink``` element, you know that this is a complete result set that contains all of the requested DriveItems. The default page size for this API is 250 items, so they all fit within a single page of results.

But the same API can return paginated responses, if the result set is larger than the page size. For example, here we're using the ```$top``` query string parameter to return only the first 10 items from the same set:

![pagination via $top parameter](static/images/root-drive-children-top.png)

In this case, we've received the first 10 DriveItems, and there is an ```@odata.nextLink``` value which we can use to query the next page of 10 items.

When working with collections in Graph APIs, your code must always check for `@odata.nextLink` to determine whether there are additional pages of data available, and understand that if the property is missing the result is the last page of available data. There is an example of this in the generator sample below.

## Using generators

The Graph API returns _pages_ of results, as demonstrated in [pagination.py](https://github.com/microsoftgraph/python-sample-pagination/blob/master/pagination.py). But in your application or service, you may want to work with a single non-paginated collection of _items_ such as messages, users, or files. In this sample, we create a Python [generator](https://wiki.python.org/moin/Generators) that hides the pagination details so that your application code can simply ask for a collection of messages and then iterate through them using standard Python idioms such as ```for messages in messages``` or ```next(message)```.

The [generator.py](https://github.com/microsoftgraph/python-sample-pagination/blob/master/generator.py) sample in this repo provides an interactive demonstration of how it works. Follow the [Installation](#installation) instructions to install the sample, and then run it as follows:

1. At the command prompt: ```python generator.py```
2. Navigate a browser to [http://localhost:5000](http://localhost:5000)
3. Choose **Connect** and authenticate with a Microsoft identity (organization account or Microsoft Account)

You'll then see the most recent message you've received:

![most recent message](static/images/generator-sample.png)

Each time you click the **Next Message** button, you'll see the next message. The ```generator()``` function in [generator.py](https://github.com/microsoftgraph/python-sample-pagination/blob/master/generator.py) handles the details as shown here:

```python
def graph_generator(session, endpoint=None):
    """Generator for paginated result sets returned by Microsoft Graph.
    session = authenticated Graph session object
    endpoint = the Graph endpoint (for example, 'me/messages' for messages,
               or 'me/drive/root/children' for OneDrive drive items)
    """
    while endpoint:
        print('Retrieving next page ...')
        response = session.get(endpoint).json()
        for item in response.get('value', None):
            yield item # return next item from this page
        endpoint = response.get('@odata.nextLink', None)
```

The key concept to understand in a Python generator is the ```yield``` statement, which returns a value but also retains the state of the generator function for the next call. We have an outer loop that steps through the paginated results (```while endpoint:```) and an inner loop (```for item in ...```) that returns the items from within each page.

To create a generator at runtime, we pass the Graph session connection object and the API endpoint for retrieving messages:

```python
MSG_GENERATOR = messages(MSGRAPH, 'me/messages')
```

Then the calling code simply uses Python's built-in ```next()``` function to retrieve messages:

```python
def generator():
    """Example of using a Python generator to return items from paginated data."""
    return {'graphdata': next(MSG_GENERATOR)}
```

We call ```next(MSG_GENERATOR)``` whenever we need the next message, and we don't need to be aware of the fact that paginated results are coming from Graph. As a practical matter, you may notice a slightly longer response time whenever a new page is retrieved (every 10th message, with the default page size of 10 messages in the sample), but the individual items within each page are returned immediately without any need to call Graph, because they're in the page of results that is being retained in the state of the generator function after each ```yield``` statement.

Python generators are recommended for working with all paginated results from Microsoft Graph. You can use the ```generator()``` function in this sample for users, groups, drive items, and other paginated responses from Graph APIs.

## Contributing

These samples are open source, released under the [MIT License](https://github.com/microsoftgraph/python-sample-pagination/blob/master/LICENSE). Issues (including feature requests and/or questions about this sample) and [pull requests](https://github.com/microsoftgraph/python-sample-pagination/pulls) are welcome. If there's another Python sample you'd like to see for Microsoft Graph, we're interested in that feedback as well &mdash; please log an [issue](https://github.com/microsoftgraph/python-sample-pagination/issues) and let us know!

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information, see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Resources

* [Paging Microsoft Graph data in your app](https://developer.microsoft.com/en-us/graph/docs/concepts/paging)
* [OData JSON Format Version 4.0](http://docs.oasis-open.org/odata/odata-json-format/v4.0/cs01/odata-json-format-v4.0-cs01.html)
* [Python Wiki: Generators](https://wiki.python.org/moin/Generators)
* [Python authentication samples for Microsoft Graph](https://github.com/microsoftgraph/python-sample-auth)
