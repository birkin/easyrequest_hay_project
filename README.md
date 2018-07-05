[![BUL Code Best-Practices](https://library.brown.edu/good_code/project_image/easyrequest-hay/)](https://library.brown.edu/good_code/project_info/easyrequest-hay/)


### overview ###

This code aims to improve the process of requesting [John Hay Library](https://library.brown.edu/hay/) items stored at the [Annex](http://library.brown.edu/about/annex/), the [Library's](http://library.brown.edu/) offsite storage facility.


### basic flow ###

user's experience...
- user clicks a 'request item' link that lands at this confirmation/login page
- after authenticating, the user lands at our [Aeon](https://brown.aeon.atlas-sys.com/aeonauth/FAQ.html) service

more detail flow...
- user initially lands at this confirmation/login page
- user clicks one of the three buttons: brown-shib-login, non-brown-login, cancel-and-return-to-[josiah](https://search.library.brown.edu/)-page
    - `brown-shib-login` will bring up shibboleth, make a request on behalf of the user in [Sierra](https://www.iii.com/products/sierra-ils/), and land the user at a pre-filled-out Aeon request-form
        - a 'staff-note' field in the Aeon request-form will indicate that a request has been placed in Sierra
    - `non-brown-login` will prompt the user to log into her Aeon account, and land her at a pre-filled-out Aeon request-form
    - `cancel-and-return` will return the user to the referring catalog bib-page


### stats ###

- A stats url offering a basic usage count for a given date-range is available in the format of:

        scheme://host/easyrequest_hay/stats_api/?start_date=2018-07-01&end_date=2018-07-31
- Dates are inclusive: as shown in the start and end timestamps, all requests in the start and end date will be counted.
- Invalid parameters or dates will display a 400/Bad-Request response, with an example of a good url.
- All entries start with a 'disposition' status of `initial_landing`. That disposition is then updated based on which of the three buttons the user clicks (brown-shib-login, non-brown-login, cancel-and-return-to-josiah).
    - Note that the `to_aeon...` dispositions do not indicate the user fully submitted the pre-filled out Aeon request-form; rather, they are simply indications of the button the user clicked from the confirmation/login landing page.
    - High counts of `initial_landing` _could_ mean that one of the goals of this annex-hay project is being realized: to help ensure users are aware that special-collections materials must be viewed in the staffed and monitored special-collections reading-room.


### contacts ###

- policy: ann_dodge at brown dot edu
- programming: birkin_diana at brown dot edu


---
