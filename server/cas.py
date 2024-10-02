# ----------------------------------------------------------------------
# CASClient.py
# Authors: Alex Halderman, Scott Karlin, Brian Kernighan, Bob Dondero
# ----------------------------------------------------------------------

from urllib.request import urlopen
from urllib.parse import quote
from re import sub
from flask import request, session, redirect, abort


class CASClient:
    # Initialize a new CASClient object so it uses the given CAS
    # server, or fed.princeton.edu if no server is given.

    def __init__(self, url="https://fed.princeton.edu/cas/"):
        self.cas_url = url

    # Return the URL of the current request after stripping out the
    # "ticket" parameter added by the CAS server.

    def stripTicket(self):
        url = request.url
        if url is None:
            return "something is badly wrong"
        url = sub(r"ticket=[^&]*&?", "", url)
        url = sub(r"\?&?$|&$", "", url)
        return url

    # Return True if user is logged in

    def is_logged_in(self):
        return "username" in session

    # Validate a login ticket by contacting the CAS server. If
    # valid, return the user's username; otherwise, return None.

    def validate(self, ticket):
        val_url = (
            self.cas_url
            + "validate"
            + "?service="
            + quote(self.stripTicket())
            + "&ticket="
            + quote(ticket)
        )
        r = urlopen(val_url).readlines()  # returns 2 lines
        if len(r) != 2:
            return None
        firstLine = r[0].decode("utf-8")
        secondLine = r[1].decode("utf-8")
        if not firstLine.startswith("yes"):
            return None
        return secondLine

    # Authenticate the remote user, and return the user's username.
    # Do not return unless the user is successfully authenticated.

    def authenticate(self):

        # If the user's username is in the session, then the user was
        # authenticated previously.  So return the user's username.
        if "username" in session:
            return session.get("username").lower().strip()

        # If the request contains a login ticket, then try to
        # validate it.
        ticket = request.args.get("ticket")
        if ticket is not None:
            username = self.validate(ticket)
            if username is not None:
                # The user is authenticated, so store the user's
                # username in the session.
                session["username"] = username
                return username.lower().strip()

        # The request does not contain a valid login ticket, so
        # redirect the browser to the login page to get one.
        login_url = self.cas_url + "login" + "?service=" + quote(self.stripTicket())

        abort(redirect(login_url))

    # Logout the user.

    def logout(self):
        # Delete the user's username from the session.
        session.pop("username")
        # Redirect the browser to the application's home page.
        abort(redirect("/"))


# -----------------------------------------------------------------------


def main():
    print("CASClient does not run standalone")


if __name__ == "__main__":
    main()