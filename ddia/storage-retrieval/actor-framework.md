# Actor Framework Deep Dive

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Actor Model Fundamentals](#actor-model-fundamentals)
4. [Real-World Examples](#real-world-examples)
5. [Popular Actor Frameworks](#popular-actor-frameworks)
6. [Code Examples](#code-examples)
7. [Advantages and Disadvantages](#advantages-and-disadvantages)
8. [Use Cases](#use-cases)
9. [Best Practices](#best-practices)
10. [References and Further Reading](#references-and-further-reading)

## Introduction

The Actor Framework is a mathematical model of concurrent computation that treats "actors" as the fundamental unit of computation. Unlike traditional object-oriented programming where objects interact through method calls, actors communicate exclusively through asynchronous message passing.

**Key Quote**: _"An actor model is a programming model for concurrency in a single process. Rather than dealing with threads (and their complications), logic is encapsulated in actors."_ - From "Designing Data-Intensive Applications"

## Core Concepts

### What is an Actor?

An actor is an independent computational entity that:

- **Encapsulates state**: Each actor maintains its own private state
- **Processes messages**: Actors respond to messages sent by other actors
- **Is location transparent**: Actors can be local or distributed across networks
- **Follows the "share nothing" principle**: No shared mutable state between actors

### Actor Lifecycle

```
[Created] → [Running] → [Suspended] → [Terminated]
     ↑         ↓           ↑
     └─────[Restarted]────┘
```

## Actor Model Fundamentals

### The Three Pillars

1. **Message Passing**: All communication happens via immutable messages
2. **Isolation**: Actors don't share state; each has its own memory space
3. **Supervision**: Actors form hierarchies where parents supervise children

### Actor Capabilities

When an actor receives a message, it can:

1. **Send messages** to other actors
2. **Create new actors** (spawn children)
3. **Change its behavior** for processing future messages

## Real-World Examples

### 1. Banking System

Think of a bank with multiple tellers (actors):

- Each **teller** is an actor handling customer requests
- **Customer accounts** are actors maintaining balance state
- **Transaction processor** is an actor coordinating transfers
- If one teller has an issue, others continue working (fault isolation)

### 2. Chat Application

- Each **user** is an actor with their own message queue
- **Chat rooms** are actors maintaining participant lists
- **Message router** actors handle delivery
- Users can join/leave without affecting others

### 3. Game Server

- Each **player** is an actor with position, health, inventory
- **Game world regions** are actors managing local state
- **NPC (Non-Player Characters)** are actors with AI behavior
- **Combat system** actors handle damage calculations

## Popular Actor Frameworks

### 1. Akka (JVM - Scala/Java)

- Most mature actor framework
- Built-in clustering and persistence
- Used by: LinkedIn, PayPal, Samsung

### 2. Erlang/OTP

- Original actor model implementation
- "Let it crash" philosophy
- Used by: WhatsApp, Discord, RabbitMQ

### 3. Actor Framework (.NET)

- Microsoft's implementation for .NET
- Integrated with Azure Service Fabric

### 4. Orleans (Microsoft)

- Virtual actors with automatic activation
- Used by: Halo services, Skype

### 5. Pykka (Python)

- Python implementation of actor model
- Good for prototyping

## Code Examples

### Basic Actor in Akka (Scala)

```scala
import akka.actor.{Actor, ActorSystem, Props}

// Define messages
case class Greet(name: String)
case class GreetingReply(message: String)

// Define actor
class GreeterActor extends Actor {
  def receive = {
    case Greet(name) =>
      println(s"Hello $name!")
      sender() ! GreetingReply(s"Hello $name!")
  }
}

// Usage
object ActorExample extends App {
  val system = ActorSystem("GreeterSystem")
  val greeter = system.actorOf(Props[GreeterActor], "greeter")

  greeter ! Greet("World")

  system.terminate()
}
```

### Bank Account Actor Example (Akka)

```scala
import akka.actor.{Actor, ActorRef, Props}

// Messages
case class Deposit(amount: Double)
case class Withdraw(amount: Double)
case class GetBalance()
case class Balance(amount: Double)

class BankAccountActor extends Actor {
  private var balance: Double = 0.0

  def receive = {
    case Deposit(amount) =>
      balance += amount
      println(s"Deposited $amount. New balance: $balance")

    case Withdraw(amount) =>
      if (balance >= amount) {
        balance -= amount
        println(s"Withdrew $amount. New balance: $balance")
      } else {
        println(s"Insufficient funds. Current balance: $balance")
      }

    case GetBalance() =>
      sender() ! Balance(balance)
  }
}

// Usage
val account = system.actorOf(Props[BankAccountActor], "account")
account ! Deposit(100.0)
account ! Withdraw(30.0)
account ! GetBalance()
```

### Simple Erlang Actor

```erlang
-module(counter).
-export([start/0, increment/1, get_value/1]).

% Start a counter actor
start() ->
    spawn(fun() -> loop(0) end).

% Main actor loop
loop(Count) ->
    receive
        {increment, From} ->
            NewCount = Count + 1,
            From ! {ok, NewCount},
            loop(NewCount);
        {get_value, From} ->
            From ! {value, Count},
            loop(Count);
        stop ->
            ok
    end.

% Helper functions
increment(Pid) ->
    Pid ! {increment, self()},
    receive
        {ok, Value} -> Value
    end.

get_value(Pid) ->
    Pid ! {get_value, self()},
    receive
        {value, Value} -> Value
    end.
```

### Python Actor with Pykka

```python
import pykka

class CalculatorActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.result = 0

    def on_receive(self, message):
        if message.get('operation') == 'add':
            self.result += message['value']
            return {'result': self.result}
        elif message.get('operation') == 'multiply':
            self.result *= message['value']
            return {'result': self.result}
        elif message.get('operation') == 'get':
            return {'result': self.result}

# Usage
if __name__ == '__main__':
    actor_system = pykka.ActorSystem('CalculatorSystem')
    calculator = actor_system.actor_of(CalculatorActor)

    # Send messages
    result1 = calculator.ask({'operation': 'add', 'value': 5})
    result2 = calculator.ask({'operation': 'multiply', 'value': 3})
    final = calculator.ask({'operation': 'get'})

    print(f"Final result: {final['result']}")  # Output: 15

    actor_system.shutdown()
```

## Advantages and Disadvantages

### Advantages

1. **Fault Tolerance**: One actor's failure doesn't crash the system
2. **Scalability**: Easy to distribute across machines
3. **Concurrency**: Natural handling of concurrent operations
4. **Debugging**: Easier to reason about isolated state
5. **Hot Code Swapping**: Can update actors without stopping the system

### Disadvantages

1. **Complexity**: Additional abstraction layer
2. **Performance Overhead**: Message passing has costs
3. **Memory Usage**: Each actor has its own mailbox
4. **Learning Curve**: Different programming paradigm
5. **Debugging**: Message flows can be hard to trace

## Use Cases

### Ideal Use Cases

1. **High-Concurrency Systems**: Web servers, game servers
2. **Distributed Systems**: Microservices, cluster computing
3. **Real-time Systems**: Trading platforms, IoT systems
4. **Fault-Tolerant Systems**: Telecom, financial systems
5. **Event-Driven Architectures**: Stream processing, notifications

### Not Suitable For

1. **CPU-intensive computations**: Single-threaded processing
2. **Simple CRUD applications**: Overhead not justified
3. **Tight coupling requirements**: Shared state needed
4. **Small-scale applications**: Complexity overhead

## Best Practices

### 1. Design Principles

```scala
// Good: Immutable messages
case class UserRegistration(email: String, name: String)

// Bad: Mutable messages
class UserRegistration {
  var email: String = _
  var name: String = _
}
```

### 2. Actor Hierarchies

```
                [Root Guardian]
                       |
              [User Guardian]
                   /       \
        [User Manager]    [Session Manager]
           /    |   \           |
    [User1] [User2] [User3]  [Sessions]
```

### 3. Message Design

```scala
// Good: Specific, immutable messages
sealed trait BankingMessage
case class Deposit(accountId: String, amount: BigDecimal) extends BankingMessage
case class Withdraw(accountId: String, amount: BigDecimal) extends BankingMessage

// Bad: Generic, mutable messages
case class BankOperation(var operation: String, var data: Map[String, Any])
```

### 4. Error Handling

```scala
class SupervisorActor extends Actor {
  override val supervisorStrategy = OneForOneStrategy() {
    case _: ArithmeticException => Resume
    case _: NullPointerException => Restart
    case _: IllegalArgumentException => Stop
    case _: Exception => Escalate
  }

  def receive = {
    case CreateChild(name) =>
      val child = context.actorOf(Props[WorkerActor], name)
      context.watch(child)
  }
}
```

## Actor vs. Other Concurrency Models

| Model           | State Sharing   | Communication      | Fault Isolation |
| --------------- | --------------- | ------------------ | --------------- |
| **Actors**      | None (isolated) | Message passing    | High            |
| **Threads**     | Shared memory   | Direct calls       | Low             |
| **Async/Await** | Shared memory   | Callbacks/Promises | Medium          |
| **CSP (Go)**    | Channels        | Channel passing    | Medium          |

## Real-World Architecture Example: E-commerce System

```
[Order Manager Actor]
        |
        ├── [Inventory Actor] ──── [Warehouse Actors]
        ├── [Payment Actor] ────── [Payment Gateway Actors]
        ├── [Shipping Actor] ───── [Shipping Provider Actors]
        └── [Notification Actor] ── [Email/SMS Actors]
```

Each component is isolated, can be scaled independently, and failures in one area don't affect others.

## References and Further Reading

### Books

1. **"Designing Data-Intensive Applications"** by Martin Kleppmann
   - Chapter on Actor Systems and Message Passing
2. **"Reactive Design Patterns"** by Roland Kuhn and Jamie Allen
   - Comprehensive patterns for reactive systems
3. **"Programming Erlang"** by Joe Armstrong
   - From the creator of Erlang and the actor model
4. **"Akka in Action"** by Raymond Roestenburg and Rob Bakker
   - Practical guide to building actor systems

### Online Resources

1. **Akka Documentation**: https://akka.io/docs/
2. **Erlang/OTP Guide**: https://www.erlang.org/doc/
3. **Microsoft Orleans**: https://docs.microsoft.com/en-us/dotnet/orleans/
4. **Actor Model Wikipedia**: https://en.wikipedia.org/wiki/Actor_model

### Research Papers

1. **"A Universal Modular Actor Formalism for Artificial Intelligence"** - Carl Hewitt (1973)
   - Original actor model paper
2. **"Actors: A Model of Concurrent Computation in Distributed Systems"** - Gul Agha (1985)
   - Foundational thesis on actor systems

### Videos and Talks

1. **"Hewitt, Meijer and Szyperski: The Actor Model"** - Channel 9
2. **"The Actor Model in 10 Minutes"** - Brian Storti
3. **"Building Reactive Systems with Akka"** - Lightbend

### Frameworks and Libraries

1. **Akka** (Scala/Java): https://akka.io/
2. **Erlang/OTP**: https://www.erlang.org/
3. **Orleans** (.NET): https://github.com/dotnet/orleans
4. **Actor Framework** (.NET): https://github.com/Danthar/actor-framework-dotnet
5. **Pykka** (Python): https://github.com/jodal/pykka
6. **Actor Model** (Rust): https://github.com/actix/actix
7. **Proto.Actor** (Go/.NET/Java): https://proto.actor/

### Community and Forums

1. **Akka Community**: https://discuss.lightbend.com/
2. **Erlang Forums**: https://erlangforums.com/
3. **Actor Model Reddit**: https://www.reddit.com/r/ActorModel/

---

_These notes provide a comprehensive foundation for understanding actor frameworks. Start with simple examples and gradually explore more complex patterns as you become comfortable with the actor mindset._
