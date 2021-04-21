# Notes

Using a state machine with the api monitor won't work because there will be no good mechanism to fire the state machine.  Additionally, the current code would also require changes as it looks in the lambda execution environment for the parameters to select the correct endpoint.

Therefore, the state machine experiment is terminated.
