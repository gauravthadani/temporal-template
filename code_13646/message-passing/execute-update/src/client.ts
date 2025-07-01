// @@@SNIPSTART typescript-update-client
import { Connection, Client, WithStartWorkflowOperation } from '@temporalio/client';
import { counter, fetchAndAdd, done } from './workflows';
import { nanoid } from 'nanoid';

async function run() {
  const connection = await Connection.connect({ address: 'localhost:7233' });
  const client = new Client({ connection });

  const handle = await client.workflow.start(counter, {
    taskQueue: 'my-task-queue',
    args: [],
    workflowId: 'workflow-' + nanoid(),

  });
  console.log(`Started workflow ${handle.workflowId}`);

  // // // Send the 'fetchAndAdd' update with the value `1` as input.
  const prevValue = await handle.executeUpdate(fetchAndAdd, { args: [1] });
  // console.log(`incrementing counter; previous value was ${prevValue}`);

  // // Send the 'fetchAndAdd' update with invalid input.
  // const invalidArg = -1;
  // try {
  //   await handle.executeUpdate(fetchAndAdd, { args: [invalidArg] });
  // } catch (error) {
  //   console.log(`Update argument ${invalidArg} was rejected: ${error}`);
  // }

  // // Send the 'done' update to allow the workflow to complete.
  // await handle.executeUpdate(done);

  // const workflowId = 'workflow-' + nanoid();


  // const startWorkflowOperation = new WithStartWorkflowOperation(counter, {
  //   workflowId,
  //   taskQueue: 'my-task-queue',
  //   workflowIdConflictPolicy: 'FAIL',
  // });



  // // const result = await client.workflow.executeUpdateWithStart('fetchAndAdd', { args: [1], startWorkflowOperation });
  // const handle = await client.workflow.startUpdateWithStart('fetchAndAdd', { args: [1], waitForStage: "ACCEPTED", startWorkflowOperation });
  // console.log(`Started workflow ${handle.workflowId}`);

  // console.log(`Final counter value is ${result}`);
  console.log(`Final counter value is ${await handle.result()}`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
// @@@SNIPEND
