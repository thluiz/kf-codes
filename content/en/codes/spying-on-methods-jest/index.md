---
title: "Spying (on) Methods with Jest"
date: "2021-07-13"
description: "Spying on methods to check application logic"
tags: ["technical", "tests", "javascript"]
featureimage: "spy-methods-cover.jpeg"
featureimagealt: "Spy methods with Jest"
canonicalURL: "https://silva.thluiz.com/posts/spying-on-methods-jest/"
silvaeSlug: "spying-on-methods-jest"
silvaeCommit: "8c5583805d153c511bda20803892e40f806d6020"
---
### How mocks make it easy to ensure your application logic

It's easy to test your application when your domain layer is decoupled from other:

For example, let's imagine the following scenario:

> In a Race Game, when the Car hit an obstacle, the player will go back a couple of yards, and the barrier will be removed

### The Pseudo-code

We have a `Game` class that receives the `Player` and the `ObstacleManager`:

```javascript
public class Game {

  public Game(Player player, ObstacleManager obstacleManager) {
    (...) /* Setup game, objects, etc */
  }

  public class updateGameState() {
    const collision = player.checkCollision(obstacleManager);

    if(collision) {
      obstacleManager.Remove(collision.Obstacle);
      player.Knockback();
    }
  }
}
```

### The Test - the slow way:

The direct (aka: "slow") approach is to instantiate the objects directly

```javascript
describe("Game Tests", () => {
  test("The player should hit obstacle in same position", () => {
    const obstacle = new Obstacle(0,0); /*creating objects with the position*/
    const obstacleManager = new ObstacleManager([ obstacle ]);
    const player = new Player(0, 0);

    const collision = player.checkCollision(obstacleManager);

    expect(collision).toBe(obstacle);
  });

  test("The player should have a Knockback if hit an obstacle", () => {
    const obstacle = new Obstacle(0,0); /*creating objects with the position*/
    const obstacleManager = new ObstacleManager([ obstacle ]);
    const player = new Player(0, 0);

    const game = new Game(player, obstacleManager);
    game.updateGameState();

    expect(player.Knockbacked).toBe(true);
  });
});
```

This kind of approach is still valid (it's better to have some tests than no test at all), but it has some issues:

-   Your tests may become brittle over time - Every change to the entities (player, obstacles, managers) may require changes in all tests;
-   The Entities may not be so easy to set up - The Player may rely on Canvas, EventListeners, or Network, etc. to be constructed;
-   You are mixing player logic with obstacle manager logic. Both entities are coupled by these tests;
-   `Knockback` can be an internal/private property that we'll need to expose just to test (information leak);

Fourtnelly, Jest has powerful mechanisms that let you Mock even your import statements:

### The Test - the fast (decoupled) way:

We'll need additional steps to setup the mocks in Jest, but it'll be payed over time:

```javascript
import { Player } from "../Entities/Player";
import { ObstacleManager } from "../Entities/Obstacles/ObstacleManager";

/* STEP 1 : Setup what jest will be mocking */
jest.mock("../Entities/Player");
jest.mock("../Entities/Obstacles/ObstacleManager");

describe("Game Tests", () => {

  beforeEach(() => {
    /* STEP 2 : Clear all instances between tests */
    Player.mockClear();
    ObstacleManager.mockClear();
  });

  test("The player should have a Knockback if hit an obstacle", () => {
    /* STEP 3 : Creating Spies */
    const knockbackSpy = jest.fn();
    Player.mockImplementation(() => {
      return { checkCollision: (manager) => { return {}; },
                Knockback: knockbackSpy };
    });

    // Jest will take care of injecting the dependencies where needed
    const game = new Game();

    game.updateGameState();

    expect(knockbackSpy).toBeCalled();
  });
});
```

Lots of things happening here, but we can summarize as:

1.  Step 1: on line 5, it's configuring Jest to replace the import of the Player and ObstacleManager with Mocks;
2.  Step 2: since your Mocks are somehow globals, We are ensuring that they are reset before each test;
3.  Step 3 - This is the tricky and not so obvious part (and why We named this post 😜): Our `Game` class is decoupled from `Player` and `ObstacleManager`, so you can spy on methods that the game is manipulating and test just the game logic itself;

The advantages of this approach:

-   This test can focus in the game logic itself because is isolated from the entities. The Game object just need to know the interface that the objects will be using (here represented by its functions);
-   Again, The entities itself don't need to know about it other. The `Player` is not coupled with the `ObstacleManager` anymore, we are just using the "interface" method CheckCollision to ensure that our Game have the appropriate logic;
-   We don't need to leak information from the `Player`, we can check, with the spy function, that our application is calling the `Knockback` method;

Now it's easier to write the test for the second statement from our requirement:

```javascript
  test("The Obstacle should be removed if hit by a Player", () => {
    const obstacle = {};
    const removeSpy = jest.fn();
    Player.mockImplementation(() => {
      return { checkCollision: (manager) => { return { Obstacle: obstacle }; },
                Knockback: jest.fn() };
    });

    ObstacleManager.mockImplementation(() => {
      return { remove: (obstacle) => removeSpy };
    });

    const game = new Game();
    game.updateGameState();

    /* the Method */
    expect(removeSpy).toBeCalledWith(obstacle);
  });
```

### Source

-   <https://jestjs.io/docs/es6-class-mocks>

### Credits

-   Revision by [Henrique Jardim](https://twitter.com/henriquejardim)
