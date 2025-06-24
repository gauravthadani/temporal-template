// @@@SNIPSTART typescript-update-workflow
import * as wf from '@temporalio/workflow';

import type * as activities from './activities';
import { sleep } from '@temporalio/activity';
// import process from 'process';

// Define an update that takes a number as input and returns a number.
export const fetchAndAdd = wf.defineUpdate<number, [number]>('fetchAndAdd');
// Define a second update that we will use to complete the workflow.
export const done = wf.defineUpdate('done');

const { greet } = wf.proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
  retry: {
    maximumAttempts: 3
  }
});

export async function counter(): Promise<number> {
  let count = 0;
  let shouldComplete = false;

  // Define an update validator that rejects negative inputs to the update.
  const validator = (arg: number) => {
    if (arg < 0) {
      throw new Error('Argument must not be negative');
    }

  };


  // Define the update handler implenting the fetchAndAdd operation. Note that
  // an update can mutate workflow state, and return a value.
  const handler = (arg: number) => {
    const prevCount = count;
    count += arg;
    return prevCount;
  };

  // Register the handler and validator for the 'fetchAndAdd' update.
  wf.setHandler(fetchAndAdd, handler, { validator });

  // Register the handler for the 'done' update.
  wf.setHandler(done, () => {
    shouldComplete = true;
  });
  //  while (true) {
  //   // statements if the condition is true 
  // }

  const res = await greet('Temporal');
  wf.log.info(`Greeting: ${res}`);

 


  await wf.condition(() => shouldComplete);

  return count;
}
// @@@SNIPEND
