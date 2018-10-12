import javax.swing.*;

import static java.lang.Integer.min;

public class RouterNode {
  private int myID;
  private GuiTextArea myGUI;
  private RouterSimulator sim;
  private int[] costs = new int[RouterSimulator.NUM_NODES];

  //--------------------------------------------------
  public RouterNode(int ID, RouterSimulator sim, int[] costs) {
    myID = ID;
    this.sim = sim;
    myGUI =new GuiTextArea("  Output window for Router #"+ ID + "  ");

    System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);
    for (int i = 0; i < costs.length; i++){
      if (ID != i){
        costs[i] = RouterSimulator.INFINITY;
      }
      else{
        costs[i] = 0;
      }
    }
  }

  //--------------------------------------------------
  public void recvUpdate(RouterPacket pkt) {
    for (int i = 0; i < costs.length; i++){
        costs[i] = min(pkt.mincost[i] + costs[pkt.sourceid], costs[i]);
    }
  }
  

  //--------------------------------------------------
  private void sendUpdate(RouterPacket pkt) {
    sim.toLayer2(pkt);

  }
  

  //--------------------------------------------------
  public void printDistanceTable() {
	  myGUI.println("Current table for " + myID +
			"  at time " + sim.getClocktime());
  }

  //--------------------------------------------------
  public void updateLinkCost(int dest, int newcost) {
  }

}
