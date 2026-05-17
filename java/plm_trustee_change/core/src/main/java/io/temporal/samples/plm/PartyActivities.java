package io.temporal.samples.plm;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.Optional;

@ActivityInterface
public interface PartyActivities {

  @ActivityMethod
  Optional<String> searchParty(String name);

  @ActivityMethod
  String createParty(String name, String documentRef);

  @ActivityMethod
  void setAmlVerified(String partyId);

  @ActivityMethod
  void addTrusteeRelationship(String trustId, String partyId);

  @ActivityMethod
  void removeTrusteeRelationship(String trustId, String partyId);

  @ActivityMethod
  boolean rulesEngineCheck(String intent, String trustId, String partyId);

  @ActivityMethod
  void notifyAccountAuthorities(String trustId, String outgoingTrusteeId, String incomingTrusteeId);
}
