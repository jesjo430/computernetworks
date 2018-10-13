import javax.swing.*;
import java.util.ArrayList;
import java.util.List;

public class RouterNode {
  private int myID;
  private GuiTextArea myGUI;
  private RouterSimulator sim;
  private int[] costs = new int[RouterSimulator.NUM_NODES];
  private int[][] distanceTable = new int[RouterSimulator.NUM_NODES][];
  private List<Integer> neighbourID = new ArrayList<Integer>();
  private int[] route = new int[RouterSimulator.NUM_NODES];

  //--------------------------------------------------
  public RouterNode(int ID, RouterSimulator sim, int[] costs) {
    myID = ID;
    this.sim = sim;
    myGUI = new GuiTextArea("  Output window for Router #"+ ID + "  ");

    System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);

    for (int i = 0; i < costs.length; i++){
      if ((costs[i] != RouterSimulator.INFINITY) || (costs[i] != 0)){
        neighbourID.add(i);
        route[i] = i;
      }
    }
    route[myID] = myID;

    for (int i = 0; i < RouterSimulator.NUM_NODES; i++){
      for (int j = 0; j < neighbourID.size(); j++){
        distanceTable[i][j] = RouterSimulator.INFINITY;
      }
    }
    sendPacketToNeighbours(myID);
  }

  //--------------------------------------------------
  public void recvUpdate(RouterPacket pkt) {
    boolean hasChanged = false;
    if(distanceTable[pkt.sourceid] != pkt.mincost){
      distanceTable[pkt.sourceid] = pkt.mincost;
      hasChanged = true;
    }

    for (int i = 0; i < costs.length; i++){
        if (pkt.mincost[i] + costs[pkt.sourceid] < costs[i]){
          costs[i] = pkt.mincost[i] + costs[pkt.sourceid];
          route[i] = pkt.sourceid;
        }
    }
    if (hasChanged){
      sendPacketToNeighbours(myID);
    }
  }

  //--------------------------------------------------
  private void sendUpdate(RouterPacket pkt) {
    sim.toLayer2(pkt);

  }

  //--------------------------------------------------
  public void printDistanceTable() {
    myGUI.println("Current state for " + myID +
            "  at time " + sim.getClocktime());

    String destinationString = "    dst |    ";
    String costString = " cost   |    ";
    String routeString = " route  |    ";

    for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
      destinationString += i + "       ";
      costString += costs[i] + "       ";
      routeString += route[i] + "       ";
    }

    myGUI.println("\nDistancetable:");
    myGUI.println(F.format(destinationString, destinationString.length()));
    myGUI.println("------------------------------");

    String tableRow;
    for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
      tableRow = " nbr  " + i + " |  ";
      for (int j = 0; j < RouterSimulator.NUM_NODES; j++) {
        tableRow += distanceTable[i][j] + "       ";
      }
      myGUI.println(F.format(tableRow, tableRow.length()));
    }
    myGUI.println("\nOur distance vector and route");
    myGUI.println(F.format(destinationString, destinationString.length()));
    myGUI.println("------------------------------");
    myGUI.println(F.format(costString, costString.length()));
    myGUI.println(F.format(routeString, routeString.length()));
  }

  //--------------------------------------------------
  public void updateLinkCost(int dest, int newcost) {
  }

  private void sendPacketToNeighbours(int ID){
    for (int i = 0; i < neighbourID.size(); i++){
      RouterPacket pkt = new RouterPacket(ID, neighbourID.get(i), costs);
      sendUpdate(pkt);
    }
  }
}
