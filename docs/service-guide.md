# Service Guide

## Folder/File Structure

- @/services/feature-name/
  - module-name/
    - sub-module-name/
      - ...
    - module-name.input.ts
    - module-name.schema.ts
    - module-name.router.ts
    - module-name.repository.ts
    - module-name.service.ts
  - feature-name.input.ts
  - feature-name.schema.ts
  - feature-name.router.ts
  - feature-name.repository.ts
  - feature-name.service.ts

## Seperation of Concerns

- Input file is for (Zod) validation
- Schema file is for database schema
- Router file is for creating tRPC procedures
- Repository file is for database calls
- Service file is for everything the end-user (developer) uses.

## Example

The following is an example of how a service file looks. Though this is perfectly applicable to how a repository file should look as well. Same syntax, same structure, same best practices. Just that the repository should be the only file that contains any database or third party API calls. The service file should only include the business logic.

```typescript
// @/services/<feature>/<feature>.service.ts
import "server-cli-only";

import Logger from "@/utils/logger"
import { jts } from "@/lib/utils";

class FeatureService {
  // The logger should be initialized with a string as the context instead of class name, because class names get serialized at compile time.
  private readonly logger = new Logger("FeatureService");
  private readonly repository: FeatureRepository;
  // The module files are identical, the only difference is that the module service does not export an instance of itself like at the end of this file. But instead exports the class so that an instance can be created under the head-service.
  // All modules should be public and accessible with the following pattern -> featureService.module.<moduleFunction>()
  public module: ModuleService;


  constructor() {
    this.module = new ModuleService();
    this.repository = new FeatureRepository();
  }

  // Every function that takes input should have a params object with all the params inside it, otherwise leave it empty.
  public async create(params: { /* ... */ }) {
    const result = /* ... */

    if (/* condition */) {
      // Errors should be handled as per the following lines.
      // The message should be stored in a variable like so.
      const errorMessage = "Error message goes right here."

      // Log the error message out as an error properly like so with the params and function name prefixing the errorMessage. Seperated by a ": ".
      this.logger.error(`create(${jts(params)}): ${errorMessage}`)

      // Then throw the appropriate error.
      throw new Error(errorMessage);
    }

    this.logger.debug(`create(${jts(params)}) -> ${jts(params)}`)
    return result;
  }

  // Ideally the function names should roughly match up to the C.R.U.D. pattern.
  public async read(parmas: { /* ... */ }) { /* ... */ }
  public async update(parmas: { /* ... */ }) { /* ... */ }
  public async delete(parmas: { /* ... */ }) { /* ... */ }
}

export const featureService = new FeatureService();
```

This is basically the only other type of file template needed - the router file. The input and schema files should just have the definitions of the different variables needed such as validators and schemas defined and exported with no real patterns or conventions.

```typescript
// @/services/<feature>/<feature>.router.ts
import "server-cli-only";

import { createTRPCRouter, protectedProcedure } from "@/services/trpc";
import { createValidator } from "@/services/<feature>/<feature>.input";
import { featureService } from "@/services/<feature>/<feature>.service";

export const serviceRouter = createTRPCRouter({
  create: protectedProcedure // Choose between - publicProcedure, protectedProcedure, and organizationProtectedProcedure.
    .input(createValidator) // Input validation here.
    .mutation(async ({ input, ctx }) => {
      const result = await featureService.create({
        /* ... */
      });

      return result;
    }),
});
```

## Best Practices

- Every repository and service should have a logger (from `@/utils/logger`) that, most importantly, logs every error. But also that writes really verbose debug messages writing out both the params of the function and the result.
- Every function paramater should be called "params" and be an object containing every value that the function requires to compute the final result.
- If the function returns some data, then a variable or constant should be defined at, ideally, the beginning called "result". Right before the return statement there should be a debug statement printing out the params and result as per the example.
- Every related file must be in the same directory. For example: if a module has a schema or input validation it should all be in a custom `<module-name>.schema.ts` together with the rest of the module code.
- Stick to create, read, update, and delete and variations of those verbs (e.g. readAll).
- Really important that the services are split up into parts that are as simple as reasonably possible. Meaning -> split parts of a service into sub-services once there is complexity that could be abstracted into its own separate system (sub-service).
- Make sure that all the file names are consistent and that they match the pattern "[...]<service-name>.<sub-service-name>.<input|schema|router|repository|service>.ts" make sure to include all of the parent services in the file name even if you are 5 layers deep.

### Checklist

- [ ] The file/folder structure is followed properly.
- [ ] There are verbose debug messages in the service and repository files, as shown in the example.
- [ ] There's proper input validation at the router.
- [ ] The first line of the repository and service file is the following: `import "server-cli-only-cli";`
