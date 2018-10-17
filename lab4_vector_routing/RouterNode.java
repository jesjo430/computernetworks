import javax.swing.*;
import java.util.ArrayList;
import java.util.List;
public class RouterNode {
  private int myID;
  private GuiTextArea myGUI;
  private RouterSimulator sim;
  private int[] costs = new int[RouterSimulator.NUM_NODES];
  private int[] shortestPath = new int[RouterSimulator.NUM_NODES];
  private int[][] distanceTable;
  private List<Integer> neighbourID = new ArrayList<Integer>();
  private int[] route = new int[RouterSimulator.NUM_NODES];
  private int[] nodeToDistanceTableEncoding = new int[RouterSimulator.NUM_NODES];
  private boolean usePoisonReverse = true;

  //--------------------------------------------------
  public RouterNode(int ID, RouterSimulator sim, int[] costs) {
    myID = ID;
    this.sim = sim;
    myGUI = new GuiTextArea("  Output window for Router #"+ ID + "  ");

    System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);
    System.arraycopy(costs, 0, shortestPath, 0, RouterSimulator.NUM_NODES);

    for (int i = 0; i < RouterSimulator.NUM_NODES; i++){
      route[i] = RouterSimulator.INFINITY;
      if ((costs[i] != RouterSimulator.INFINITY) && (costs[i] != 0)){
        neighbourID.add(i);
        route[i] = i;
      }
      // Assume no node added.
      nodeToDistanceTableEncoding[i] = RouterSimulator.INFINITY;
    }
    route[myID] = myID;

    distanceTable = new int[neighbourID.size()][RouterSimulator.NUM_NODES];

    for (int i = 0; i < neighbourID.size(); i++){
      for (int j = 0; j < RouterSimulator.NUM_NODES; j++){
        distanceTable[i][j] = RouterSimulator.INFINITY;
      }
      nodeToDistanceTableEncoding[neighbourID.get(i)] = i;
    }
    sendPacketToNeighbours(myID);
  }

  //--------------------------------------------------
  public void recvUpdate(RouterPacket pkt) {
    int tempShortest = RouterSimulator.INFINITY;
    int tempRoute = RouterSimulator.INFINITY;
    boolean hasChanged = false;

    for (int i = 0; i < RouterSimulator.NUM_NODES; i++){
      distanceTable[nodeToDistanceTableEncoding[pkt.sourceid]][i] = pkt.mincost[i];
    }

    for (int i = 0; i < RouterSimulator.NUM_NODES; i++){
      for (int v = 0; v < neighbourID.size(); v++){
        if (distanceTable[v][i] + costs[neighbourID.get(v)] < tempShortest){
          tempShortest = distanceTable[v][i] + costs[neighbourID.get(v)];
          tempRoute = neighbourID.get(v);
        }
      }
      if (tempShortest < costs[i]){
        if (tempShortest != shortestPath[i]){
          shortestPath[i] = tempShortest;
          route[i] = tempRoute;
          hasChanged = true;
        }
      }
      else if (shortestPath[i] != costs[i]){
        shortestPath[i] = costs[i];
        route[i] = i;
        hasChanged = true;
      }
      tempShortest = RouterSimulator.INFINITY;
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

    String destinationString = "    dst  |    ";
    String costString = " cost   |    ";
    String routeString = " route |    ";

    for (int i = 0; i < RouterSimulator.NUM_NODES; i++) {
      destinationString += i + "       ";
      costString += shortestPath[i] + "       ";
      routeString += route[i] + "       ";
    }

    myGUI.println("\nDistancetable:");
    myGUI.println(F.format(destinationString, destinationString.length()));
    myGUI.println("----------------------------------------");

    String tableRow;
    for (int i = 0; i < neighbourID.size(); i++) {
      tableRow = " nbr  " + neighbourID.get(i) + " |  ";
      for (int j = 0; j < RouterSimulator.NUM_NODES; j++) {
        tableRow += distanceTable[i][j] + "       ";
      }
      myGUI.println(F.format(tableRow, tableRow.length()));
    }
    myGUI.println("\nOur distance vector and route");
    myGUI.println(F.format(destinationString, destinationString.length()));
    myGUI.println("-----------------------------------------");
    myGUI.println(F.format(costString, costString.length()));
    myGUI.println(F.format(routeString, routeString.length()));

    myGUI.println("");
    myGUI.println("");
    myGUI.println("");
    myGUI.println("");
  }

  //--------------------------------------------------
  public void updateLinkCost(int dest, int newcost) {
    costs[dest] = newcost;
    sendPacketToNeighbours(myID);
  }

  private void sendPacketToNeighbours(int ID){
    for (int i = 0; i < neighbourID.size(); i++){
      int[] poisonShortestPath = new int[RouterSimulator.NUM_NODES];
      for (int d = 0; d < RouterSimulator.NUM_NODES; d++){
        if (route[d] == neighbourID.get(i) && usePoisonReverse){
          poisonShortestPath[d] = RouterSimulator.INFINITY;
        }
        else{
          poisonShortestPath[d] = shortestPath[d];
        }
      }
      RouterPacket pkt = new RouterPacket(ID, neighbourID.get(i), poisonShortestPath);
      sendUpdate(pkt);
    }
  }
}

