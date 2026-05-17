package io.temporal.samples.plm;

import io.temporal.activity.ActivityOptions;
import io.temporal.failure.ApplicationFailure;
import io.temporal.workflow.Workflow;
import java.time.Duration;
import org.slf4j.Logger;

public class TrusteeChangeWorkflowImpl implements TrusteeChangeWorkflow {

  private final PartyActivities activities =
      Workflow.newActivityStub(
          PartyActivities.class,
          ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofMinutes(1)).build());

  private String trustDeedRef;
  private Boolean idvVerified;
  private String incomingPartyId;
  private boolean success = false;

  @Override
  public ChangeTrusteeResult execute(ChangeTrusteeRequest request) {
    Logger log = Workflow.getLogger(TrusteeChangeWorkflowImpl.class);
    log.info(
        "Change trustee on {}: {} -> {}",
        request.trustId(),
        request.outgoingTrusteeId(),
        request.incomingTrusteeName());

    incomingPartyId =
        activities
            .searchParty(request.incomingTrusteeName())
            .orElseGet(() -> onboardAsTrustee(request.incomingTrusteeName()));

    if (!activities.rulesEngineCheck("ADD_TRUSTEE", request.trustId(), incomingPartyId)) {
      throw ApplicationFailure.newNonRetryableFailure(
          "Rules engine rejected ADD_TRUSTEE", "RULE_VIOLATION");
    }
    activities.addTrusteeRelationship(request.trustId(), incomingPartyId);

    if (!activities.rulesEngineCheck(
        "REMOVE_TRUSTEE", request.trustId(), request.outgoingTrusteeId())) {
      throw ApplicationFailure.newNonRetryableFailure(
          "Rules engine rejected REMOVE_TRUSTEE", "RULE_VIOLATION");
    }
    activities.removeTrusteeRelationship(request.trustId(), request.outgoingTrusteeId());

    activities.notifyAccountAuthorities(
        request.trustId(), request.outgoingTrusteeId(), incomingPartyId);

    success = true;
    return new ChangeTrusteeResult(incomingPartyId, trustDeedRef, success);
  }

  @Override
  public ChangeTrusteeResult getCurrentResult() {
    return new ChangeTrusteeResult(incomingPartyId, trustDeedRef, success);
  }

  private String onboardAsTrustee(String name) {
    Workflow.await(() -> trustDeedRef != null);
    String partyId = activities.createParty(name, trustDeedRef);

    Workflow.await(() -> idvVerified != null);
    if (!idvVerified) {
      throw ApplicationFailure.newNonRetryableFailure("IDV failed for " + name, "IDV_FAILED");
    }

    activities.setAmlVerified(partyId);
    return partyId;
  }

  @Override
  public void trustDeedReceived(String documentRef) {
    this.trustDeedRef = documentRef;
  }

  @Override
  public void idvCompleted(boolean verified) {
    this.idvVerified = verified;
  }
}
