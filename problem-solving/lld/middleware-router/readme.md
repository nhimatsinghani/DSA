Middleware Router
a) We want to implement a middleware router for our web service, which based on the path returns different strings
Our interface for the router looks something like:
Interface Router {
Fun addRoute(path: String, result: String) : Unit;
Fun callRoute(path:String) :String;
}

Usage:
Router.addRoute(“/bar” , “result)
Router.callRoute(“/bar”) -> “result”

Scale Up 1 – Wildcards using ordered checking
Scale Up 2 – PathParams
