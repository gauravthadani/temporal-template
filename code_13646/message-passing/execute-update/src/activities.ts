import { sleep } from '@temporalio/activity';

export async function greet(name: string): Promise<string> {
  await sleep(1000); // Simulate some asynchronous operation
  return `Hello, ${name}!`;
}
