<p style="text-align: justify">Illuminate is run from shell.</p>

```shell
illuminate --help
```

    Usage: illuminate [OPTIONS] COMMAND [ARGS]...

      Framework entrypoint.

    Options:
      --version                       Show the version and exit.
      --verbosity [TRACE|DEBUG|INFO|SUCCESS|WARNING|ERROR|CRITICAL]
                                      Configure logging levels.  [default: INFO]
      --help                          Show this message and exit.

    Commands:
      manage   Framework manage group of commands.
      observe  Framework observe group of commands.

```shell
illuminate version
```

    illuminate, version 0.2.0

<p style="text-align: justify">There are two types of command groups.
<code>manage</code> and <code>observe</code>.</p>

---

## `manage`
```shell
illuminate manage --help
```

    Usage: illuminate manage [OPTIONS] COMMAND [ARGS]...

      Framework manage group of commands.

    Options:
      --help  Show this message and exit.

    Commands:
      db       Prepares relational db for ETL operations.
      project  Performs project operations.

### `project`
```shell
illuminate manage project --help
```

    Usage: illuminate manage project [OPTIONS] COMMAND [ARGS]...

      Performs project operations.

    Options:
      --help  Show this message and exit.

    Commands:
      setup  Creates a project directory with all needed files.


#### `setup`
```shell
illuminate manage project setup --help
```

    Usage: illuminate manage project setup [OPTIONS] NAME [PATH]

      Creates a project directory with all needed files.

    Options:
      --help  Show this message and exit.

| arguments | description  | default           | required |
|-----------|--------------|-------------------|----------|
| NAME      | project name | N/A               | True     |
| [PATH]    | project path | current directory | False    |

### `db`

```shell
illuminate manage db --help
```

    Usage: illuminate manage db [OPTIONS] COMMAND [ARGS]...

      Prepares relational db for ETL operations.

    Options:
      --help  Show this message and exit.

    Commands:
      populate  Populates database with fixtures.
      revision  Creates Alembic's revision file in migration directory.
      upgrade   Applies migration file to a database.

#### `revision`
```shell
illuminate manage db revision --help
```

    Usage: illuminate manage db revision [OPTIONS] [PATH]

      Creates Alembic's revision file in migration directory.

    Options:
      --revision TEXT  Alembic revision selector.  [default: head]
      --selector TEXT  Database connection selector.  [default: main]
      --url TEXT       Optional URL for databases not included in settings module.
      --help           Show this message and exit.

| arguments | description  | default           | required |
|-----------|--------------|-------------------|----------|
| [PATH]    | project path | current directory | False    |


#### `upgrade`
```shell
illuminate manage db upgrade --help
```

    Usage: illuminate manage db upgrade [OPTIONS] [PATH]

      Applies migration file to a database.

    Options:
      --revision TEXT  Alembic revision selector.  [default: head]
      --selector TEXT  Database connection selector.  [default: main]
      --url TEXT       Optional URL for databases not included in settings module.
      --help           Show this message and exit

| arguments | description  | default           | required |
|-----------|--------------|-------------------|----------|
| [PATH]    | project path | current directory | False    |

#### `populate`
```shell
illuminate manage db populate --help
```

    Usage: illuminate manage db populate [OPTIONS]

      Populates database with fixtures.

    Options:
      --fixtures PATH  Fixture files paths.  [required]
      --selector TEXT  Database connection selector.  [default: main]
      --url TEXT       Optional URL for databases not included in settings module.
      --help           Show this message and exit.

---

## `observe`
```shell
illuminate observe --help
```

    Usage: illuminate observe [OPTIONS] COMMAND [ARGS]...

      Framework observe group of commands.

    Options:
      --help  Show this message and exit.

    Commands:
      catalogue  Lists observers found in project files.
      start      Starts producer/consumer ETL process.

### `catalogue`
```shell
illuminate observe catalogue --help
```

    Usag[e: illuminate observe catalogue [OPTIONS]

      Lists observers found in project files.

    Options:
      --help  Show this message and exit

### `start`
```shell
illuminate observe start --help
```

    Usage: illuminate observe start [OPTIONS]

      Starts producer/consumer ETL process.

    Options:
      --observer TEXT  Observer selector. Leave empty to include all observers.
      --help           Show this message and exit.
