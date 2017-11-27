# Working with paginated Graph responses in Python

Some Microsoft Graph queries can return a large number of entities, more than can practically be included in a single JSON payload. In those cases, Graph _paginates_ responses to improve performance as well as developer convenience and flexibility.

This repo contains Python-based examples of how to work with Graph's paginated responses. For a high-level overview of how pagination works in Microsoft Graph, see [Paging Microsoft Graph data in your app](https://developer.microsoft.com/en-us/graph/docs/concepts/paging).

The samples in this repo use **messages** to illustrate how pagination works, but the same concepts can be applied to any Graph API that uses pagination, including [messages](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/user_list_messages), [contacts](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/user_list_contacts), [users](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/user_list), [groups](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/group_list), and others.

* [Installation](#installation)
* [Running the samples](#running-the-samples)
* [Basic concepts](#basic-concepts)
* [Using generators](#using-generators)
* [Contributing](#contributing)
* [Resources](#resources)

## Installation

/// how to install the samples and run them

## Running the samples

/// how to launch the samples
/// note these use graphrest for auth; link to the auth repo for auth options

## Basic concepts

Graph's approach to pagination for potentially large result sets uses the [odata.context](http://docs.oasis-open.org/odata/odata-json-format/v4.0/cs01/odata-json-format-v4.0-cs01.html#_Toc365464685) and [odata.nextLink](http://docs.oasis-open.org/odata/odata-json-format/v4.0/cs01/odata-json-format-v4.0-cs01.html#_Toc365464689) annotations that are defined in [OData JSON Format Version 4.0](docs.oasis-open.org/odata/odata-json-format/v4.0/cs01/odata-json-format-v4.0-cs01.html).

When you query a paginated Graph API (for example, ```me/messages```), you'll get back a JSON payload that contains these top-level elements:

* ```@odata.context``` contains a URI that identifies the type of data being returned. This value is the same for every page of the result set.
* ```@odata.nextLink``` contains a link to the next page of results. You can do a GET against that endpoint to return the next page, which will contain a link to the next page after that, and you can repeat this process until the final page, which will not have this element.
* ```value``` contains the returned data, as a list of JSON elements. In the ```me/messages``` example, this would be a list of email messages. The number of items returned is based on the page size. Each paginated API has a default page size (for example, the ```me/messages``` default is 10 messages), and you can specify a different page size if desired through use of the ```$top``` parameter. Note that the default page size and maximum page size may vary for different Graph APIs &mdash; see [Paging Microsoft Graph data in your app](https://developer.microsoft.com/en-us/graph/docs/concepts/paging) for more information.

The following diagram shows how this works in practice, using the ```me/messages``` endpoint as an example.

/// run pagination.py as covered above

![pagination example](static/images/pagination-example.png)

The [pagination.py](https://github.com/microsoftgraph/python-sample-pagination/blob/master/pagination.py) sample in this repo provides an interactive demonstration of how it works. After you install and run the sample, authenticate under your identity and you'll see the following page listing your most recent 10 messages:

![most recent 10 messages](static/images/pagination-sample.png)

The **@odata.nextLink** value links to the next page of results. Each time you click on the **Next Page** button, the next page of results is loaded. This is the fundamental behavior of paginated responses from Graph APIs.

### What if @odata.nextLink is missing?

Some Graph APIs return all of the requested entities by default, and in that case the ```@odata.nextLink``` element is not provided. The absense of this element tells you that the ```value``` element contains all entities in a single page.

For example, if there are less than 250 items in your OneDrive root folder, you will see this JSON response when you request all of the [DriveItems](https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/resources/driveitem) in the folder by doing a GET to the ```https://graph.microsoft.com/v1.0/me/drive/root/children``` endpoint:

![root drive children](static/images/root-drive-children.png)

Since there is no ```@odata.nextLink``` element, you know that this is a complete result set that contains all of the requested DriveItems. The default page size for this API is 250 items, so they all fit within a single page of results.

But the same API can also return paginated responses, if the result set is parger than the page size. For example, here we're using the ```$top``` query string parameter to return only the first 10 items from the same set:

![pagination via $top parameter](static/images/root-drive-children-top.png)

In this case, we've received the first 10 DriveItems, and there is an ```@odata.nextLink``` value which we can use to query the next page of 10 items.

As a best practice, your code should allow for the fact that ```@odata.nextLink``` may be missing, in which case there is no pagination to be handled. There is an example of this in the generator sample below.

## Using generators

The Graph API returns _pages_ of results, as demonstrated in [pagination.py](https://github.com/microsoftgraph/python-sample-pagination/blob/master/pagination.py). But in your application or service, you may want to work with a single non-paginated collection of _items_ such as messages, users, or files. In the next sample, we'll create a Python [generator](https://wiki.python.org/moin/Generators) that hides the pagination details so that your application code can simply ask for a collection of messages and then iterate through them using standard Python idioms such as ```for messages in messages``` or ```next(message)```.

The ```messages()``` function in [generator.py](https://github.com/microsoftgraph/python-sample-pagination/blob/master/generator.py) returns a generator for a specified Graph session and mail folder. The code is simple:

```python
def messages(msgraph, mailfolder=None):
    """Generator to return messages from a specified folder.
    msgraph = authenticated Graph session object
    mailfolder = name or id of mail folder; for example, 'inbox' or a
                120-character ID value. If not specified, ALL messages
                are returned, using the me/messages endpoint.
    """
    next_page = 'me/mailFolders/' + mailfolder + '/messages' if mailfolder else 'me/messages'
    while next_page:
        response = msgraph.get(next_page).json()
        for msg in response.get('value', None):
            yield msg
        next_page = response.get('@odata.nextLink', None)
```

The key concept to understand in a Python generator is the ```yield``` statement, which returns a value but also retains the state of the generator function for the next call. We have an outer loop that steps through the pages (```while next_page:```) and an inner loop (```for msg in ...```) that returns each message from withing each page.

To create the generator, we pass the Graph session connection object and a mail folder:

```python
MSG_GENERATOR = messages(MSGRAPH, 'inbox')
```

Then the calling code simply uses Python's built-in ```next()``` function to retrieve messages:

```python
@bottle.route('/generator')
@bottle.view('generator.html')
def generator():
    """Example of using a Python generator to return paginated data."""
    return {'graphdata': next(MSG_GENERATOR)}
```

After a page of results has been returned, the outer loop of the ```messages()``` function will retrieve the next page. The developer doesn't need to be aware of this, though: you can call ```next(MSG_GENERATOR)``` whenever you need the next message, without regard for the page boundaries. As a practical matter, you may notice a slightly longer response time whenever new page is retrieved (every 10th message, with the default page size of 10 messages), but the individual messages within each page are returned immediately without any need to call Graph, because they're in the page of results that is being retained in the state of the generator function after each ```yield``` statement.

Python generators are recommended for working with all paginated results from Microsoft Graph. You can use the same technique demonstrated in this sample for users, groups, drive items, and other paginated responses from Graph APIs.

## Contributing

These samples are open source, released under the [MIT License](https://github.com/microsoftgraph/python-sample-pagination/blob/master/LICENSE). Issues (including feature requests and/or questions about this sample) and [pull requests](https://github.com/microsoftgraph/python-sample-pagination/pulls) are welcome. If there's another Python sample you'd like to see for Microsoft Graph, we're interested in that feedback as well &mdash; please log an [issue](https://github.com/microsoftgraph/python-sample-pagination/issues) and let us know!

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information, see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Resources

* [Paging Microsoft Graph data in your app](https://developer.microsoft.com/en-us/graph/docs/concepts/paging)
* [OData JSON Format Version 4.0](http://docs.oasis-open.org/odata/odata-json-format/v4.0/cs01/odata-json-format-v4.0-cs01.html)
* [Python Wiki: Generators](https://wiki.python.org/moin/Generators)
* [Python authentication samples for Microsoft Graph](https://github.com/microsoftgraph/python-sample-auth)
