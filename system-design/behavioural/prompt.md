## Projects at Rippling (Previous Company) :

These are some of the complex projects that Ive undertaken in my career so far where I have taken key ownership to develop the application/framework, onboard other Rippling Teams on our framework and framed up details documentation of my product for ease of integration and cross-team communication.

### Project 1 : Approvals Framework :

I led the development of a unified approvals framework which is a Centralised App for all other Rippling Products when it comes to adding an approvals intervention in their product flow.
This involved designing and building the framework from scratch keeping in mind the extensibility of the product since multiple different teams(PTO, Spend Mgmt, Payroll, HRIS, etc) would integrate with this framework.

The project majorly involved 2 services where one was the Approvals Request Framework that orchestrated the change request over its lifecycle, sending appropriate notifications(email/slack) and made sure to reliably execute client hooks after any action is executed on the change request. The other service was the Evaluator Service which was responsible to dynamically compute the approvers of a change request given a change request object. This service interated with an RQL service(in house language to query employee-related data flexibly) and dynamically computed a set of approvers that are supposed to approve a change request

Adding extensive monitoring and logging to make sure appropriate alerts are notifying the on-call which allowed us to be pro-active instead of re-active
Leading integration of this framework with other teams where I would be the single point of contact for clarifications and process involved in the Integration from the approvals side.
I also lead and was actively involved in the project scoping and PRD review where we would actively go through incoming requirements and my job was to actively point in in-feasibilities or call-out some aspects of the requirements that could be simplified for better User Experience and Engineering
Implemented self-healing background CRON jobs that made sure that our system's state eventually reached the correct consisten state and no manual fixes are required.
I focused on driving ambiguous and complex engineering asks and converted them into simple-clarified-executable tasks which were then worked upon by me and some of the other members of the team to parallelize the execution.

A scenario where I did a tradeoff analysis and went with an approach that gave quick impact on the latency of our Bulk Action APIs was to :
-- Implement a central Read Schema Collection where we could create a materialized view of the data that was needed on our main dashboard ( for querying or rendering). All writes in the system would eventually update this central materialised collection
-- Our Bulk Action APIs were slow as they did sequential execution of every single request which increased the overall latency of the Bulk Request. This was a primary API request and it was important to make this request as snappy as possible
-- Long and Short term solutions were possible and I led the design choice of proposing a quick solution that would minimize the API latency to the required levels. The solution was to optimistically update our Materialised View Object to the required state and then do the actuall business logic updates for each of those bulk actions.
-- The front end would just fire and forget this API without waiting on the output. Since the materialized views are updated at first, the FE refetches the dashboard data to display the updated view.
-- This significantly improved the latency of the Bulk API drastically and was applauded by our users.
-- Although this approach introduced eventual consistency in the system where there could be failures after we optimistically update our Materialized Views. But we also had background CRON jobs that would keep the Materialised View as per the state of actual business entity objects.
-- This was an acceptable tradeoff as per the business requirements at that stage in the product. And that's why we went ahead with the short term solution.
-- 3-4 months down the line, we upgraded our framework to support asynchronous operations that happened when someone Approved/Rejected a Request. This meant that our Bulk Actions API no longer waits for the entire operation to complete(mainly the onApprove/onReject/onProcess hook implementations) and we would simplify add those process executions requests as events in a messaging queue. The event gets picked up by a worker that executes the hook implementations. Once this was implemented, we were able to remove the optimistic update approach and fully embrace the async hook implementation functionality

Another Project that I lead here was : Approvals Preview which involved doing a computation of the approvers for a change request and showing it to the user before they submit the request. This involved creating generic endpoints that could be used by multiple teams. We involved the use of Redis cache here which would cache the computed approvers for a change request when they computed at the time of preview. Then when the change request is submitted, we lookup in the cache and get the pre-computed list of approvers from there. This avoided re-computation of CPU intensive process that computed the list of approvers for a given change request.

Generic Feature Implementation for individual teams : Multiple teams had specific requirements/featuresets(like time sensitive approvals) that we implemented generically so that it can be leveraged by every team that integrates with our framework. So every feature/requirement was carefully adjusted and integrated from an extensibility POV.

Led Design and Implementation of Complex feature projects like improving explainability (what is happening and why it is happening. Eg, whis is "A" selected as an approver for "Z request), responsibility transfer(when "A" is terminated, then the approval requests that are pending on them for review should be transferred to appropriate delegate)

### Project 2 : Delegation Framework :

Another major project that I led, designed and implemented E2E was : Delegation Framework.
Details : We wanted to develop solution for scenarios like : when an employee goes on PTO, then the pending tasks on the employee should be delegated to another employee based on some flexible rules/policies

First step was to create a High Level System Design Document that centered around how we should develop this featureset.
There were multiple approaches outlined to solve this particular problem.
Considering some future requirements and extensibility in mind, We approached it from "builing a platform framework" instead of "Developing something to satisfy the existing requirements". This involved abstracting out a Delegation Framework that would be responsible to expose API to interact with Delegation Policies and Trigger Delegation
The encapsulated/abstracted nature of this framework connected well with the staff engineers who were reviewing the Architecture Document.
We designed this in an event-driven fashion where PTO would trigger an event. Delegation Framework would consume this event and convert it into a DelegationEvent. Check if there are any Delegation Policies configured in the system that would lead to a Delegation. If yes, then we compute the backup-employees and trigger an event to notify interested consumers. Eg : Approvals App would consume the event and execute appropriate business logic that will add the "backup-employee" as an approver to the pending approval requests on the original employee.
Similary, when their PTO is over, PTO would send another event which would be consumed by Delegation Framework, update the Delegation State as complete and trigger an event for downstream consumption ( By Approavls Service)

The above flow was proposed and architected to the Team and reviewed by some staff engineers of our Team.
This project involved interacted with multiple teams/stakeholders and keeping everyone in sync with each other regarding the progress, timelines, blockers so that the project gets delivered as expected.

## Projects at Toku ( Current Company )

I joined an early-stage payroll startup as a Senior Software Engineer to work with a lean team of software engineers.
Here, I have worked on projects that are linked with Blockchain(Web3) and also involved around working with Third Party Web3 Data Providers to
I have also worked in building and maturing their payroll/HRIS platform in order to make the end-user journey better and as automated as possible.
Designed and Developed a comprehensive Change Management system from scratch where users are able to request changes in different datasets and then the Admins are able to review these Change Requests on a unifying dashboard to quick apply the change. This also ensures that our system has an Audit log of all the Changes that have happened in the system.

The Developement process starts with laying out all the potential solutions to an ambiguous list of requirements along with the timelines for the execution so that business stakeholders that decide which engineering works best as per the delivery urgency.

Lots of team collaboration between engineers and customer-success team to understand our customer requirement and understand the root of their problems. Then automating them with the most viable solution.

Integrating with Third Party Payment Faciliators like Bridge(Acquired by Stripe for Stablecoin payments) and Ebury (for FIAT payments) to understand their API spec and how Toku can integrate with them to accomplish E2E settlement of a payroll/invoice completely on the platform

Most of the time is spent in designing the user journey and make it as simple and intuitive as possible. Then we translate those finalised flows into maintainable code over an agreed upon timeline.
