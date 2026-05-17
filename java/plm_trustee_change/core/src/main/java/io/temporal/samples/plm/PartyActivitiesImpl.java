package io.temporal.samples.plm;

import java.util.Optional;
import java.util.concurrent.ThreadLocalRandom;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PartyActivitiesImpl implements PartyActivities {

  private static final Logger log = LoggerFactory.getLogger(PartyActivitiesImpl.class);

  private static void simulateWork() {
    try {
      Thread.sleep(ThreadLocalRandom.current().nextLong(3000, 4001));
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
    }
  }

  @Override
  public Optional<String> searchParty(String name) {
    log.info("PRDD: searching for {}", name);
    simulateWork();
    return Optional.empty();
  }

  @Override
  public String createParty(String name, String documentRef) {
    log.info("CMDM: creating party {} (deed {})", name, documentRef);
    simulateWork();
    return "party-" + name.replace(' ', '-').toLowerCase();
  }

  @Override
  public void setAmlVerified(String partyId) {
    log.info("CMDM: marking {} AML verified", partyId);
    simulateWork();
  }

  @Override
  public void addTrusteeRelationship(String trustId, String partyId) {
    log.info("CMDM: link {} as trustee of {}", partyId, trustId);
    simulateWork();
  }

  @Override
  public void removeTrusteeRelationship(String trustId, String partyId) {
    log.info("CMDM: remove {} as trustee of {}", partyId, trustId);
    simulateWork();
  }

  @Override
  public boolean rulesEngineCheck(String intent, String trustId, String partyId) {
    log.info("Rules engine: {} trust={} party={}", intent, trustId, partyId);
    simulateWork();
    return true;
  }

  @Override
  public void notifyAccountAuthorities(
      String trustId, String outgoingTrusteeId, String incomingTrusteeId) {
    log.info("Notify: trust {} {} -> {}", trustId, outgoingTrusteeId, incomingTrusteeId);
    simulateWork();
  }
}
