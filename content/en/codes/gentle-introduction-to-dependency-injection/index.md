---
title: "A gentle introduction to dependency injection"
date: "2021-08-25"
description: "A seminal principle to make applications testable"
tags: ["tecnico", "solid", "architecture", "tests"]
featureimage: "dependency-injection.jpg"
featureimagealt: "Dependency injection diagram"
canonicalURL: "https://silva.thluiz.com/posts/gentle-introduction-to-dependency-injection/"
silvaeSlug: "gentle-introduction-to-dependency-injection"
silvaeCommit: "8c5583805d153c511bda20803892e40f806d6020"
---
## Objective

To test applications, We need to ensure that their parts don't depend on each other, and this principle is the key to it.

The objective here is to quickly explain dependency injection and how it can help test without diving too deep into its implementation in programming languages or frameworks.

## What is Dependency Injection:

Wikipedia summarizes Dependency Injection as:

> (...) the dependency inversion principle is a specific form of loosely coupling software modules. When following this principle, the conventional dependency relationships established from high-level, policy-setting modules to low-level, dependency modules are reversed, thus rendering high-level modules independent of the low-level module implementation details

We have a lot of complicated words here: what is dependency? Coupling? Injecting? is this a vaccine?

We refer to a dependency as something that your object needs to work. For example, A surgeon may require a scalpel, so this is a dependency to do a surgery. When the medic asks for a scalpel, bistoury, or lint and the auxiliary passes it to him/her, the auxiliary injects the needed dependencies to make a surgery.

Other real-life analogies:

-   If you want to cut something, you'll need something that can cut (Cut method in ISharp interface). It can be a knife, a scalpel, a sword, a chainsaw...
-   If you want to go to point A to B in your city, you may ask for a Uber; it doesn't matter who is your driver or the car;

I like to summarize it as the "**Hollywood principle:** Don't call us, We call You!" (I don't know who coined this, but I've traced it back to a post from [Stefano Mazzocchi](https://web.archive.org/web/20040202120126/http://www.betaversion.org/~stefano/linotype/news/38)).

### The code example

Lets think we have a Samurai and a Sword in our Game:


```javascript
class Samurai {
  constructor() {
    this.weapon = new Sword();
  }

  hit(enemy) {
    this.weapon.hit(enemy);
  }
}

class Sword : Weapon {
  hit(enemy) {
    // (...)
  }
}

class Game {
  constructor() {
    this.samurai = new Samurai();
  }
}
```

This Samurai is coupled with the Sword object; he can't use other weapons! Let's apply some Dependency Inversion:

```javascript
class Samurai {
  constructor(weapon) {
    this.weapon = weapon;
  }

  hit(enemy) {
    this.weapon.hit(enemy);
  }
}

class Sword : Weapon {
  hit(enemy) {
    // (...)
  }
}

class Game {
  constructor() {
    this.samurai = new Samurai(new Sword());
  }
}
```

Now the Samurai can use anything that is a weapon, and we can write tests for it without depending on the Sword object:

```javascript
class TestSword : Weapon {
  hit(enemy) {
    // (...) we can spy the enemy to ensure it's been hit 😜
  }
}

class Test {
  constructor() {
    this.samurai = new Samurai(new TestSword());
  }
}
```

Things can become quite complicated when dealing with multiple dependencies, that's when We can introduce a Dependency Injection framework. The general idea is to register the types and let the framework do the hard work, something like:

```javascript
class Test {
  constructor() {
    /* General idea of something to control dependencies*/
    this.di = new DependencyInjectionContainer();
    di.Register(Samurai);
    di.Register(TestSword);

    /* Here the magic happens:
     The DI container resolve its classes to concrete types.
     All dependency injection frameworks will do this somehow*/
    di.ResolveDependencies();

    this.samurai = this.di.Get(Samurai);
  }
}
```

## Summary

This is just a high-level view of Dependency Injection (DI), and We'll go back to it from time to time when implementing tests.

Going deeper into Domain-Driven Design (DDD), this principle allows us to write our Domains and Repositories without dependencies in external components. As a result, we can focus our tests on the algorithm instead of building things.

As usual, DI is not a silver bullet: You should know when to use it. Things can go out of control, and your code doesn't have anything concrete; everything is injected from some obscure configuration somewhere (yes, I'm looking at You Java/Spring). We'll try to find the right balance between abstractions and concrete types as we go.

To summarize: **Don't let your classes build dependencies; let other high-level components handle that for them.**

### Sources

-   Wikipedia <https://en.wikipedia.org/wiki/Dependency_inversion_principle>

-   Martin Fowler excellent article about DI: <https://martinfowler.com/articles/injection.html>
