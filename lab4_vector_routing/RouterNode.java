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
      route[i] = RouterSimulator.INFINITY; //initialize routes from start to be inf. 
      if ((costs[i] != RouterSimulator.INFINITY) && (costs[i] != 0)){ //If current node is neighbor
        neighbourID.add(i);
        route[i] = i;
      }
      nodeToDistanceTableEncoding[i] = RouterSimulator.INFINITY;// Assume no node added.
    }
    route[myID] = myID;

    distanceTable = new int[neighbourID.size()][RouterSimulator.NUM_NODES];

    for (int i = 0; i < neighbourID.size(); i++){
      for (int j = 0; j < RouterSimulator.NUM_NODES; j++){
        distanceTable[i][j] = RouterSimulator.INFINITY; //initialize dist. table from start to be inf. 
      }
      nodeToDistanceTableEncoding[neighbourID.get(i)] = i; //Add neighbors
    }
    sendPacketToNeighbours(myID); //Update neighors with news
  }

  //--------------------------------------------------
  public void recvUpdate(RouterPacket pkt) {
    int tempShortest = RouterSimulator.INFINITY;
    int tempRoute = RouterSimulator.INFINITY;
    boolean hasChanged = false;

    for (int i = 0; i < RouterSimulator.NUM_NODES; i++){
      distanceTable[nodeToDistanceTableEncoding[pkt.sourceid]][i] = pkt.mincost[i]; //Add new cost to dist. table
    }

    for (int i = 0; i < RouterSimulator.NUM_NODES; i++){
      for (int v = 0; v < neighbourID.size(); v++){
        if (distanceTable[v][i] + costs[neighbourID.get(v)] < tempShortest){
          tempShortest = distanceTable[v][i] + costs[neighbourID.get(v)]; //Bellman-ford equation
          tempRoute = neighbourID.get(v);
        }
      }
      if (tempShortest < costs[i]){ //If any neighbor has less costly path
        if (tempShortest != shortestPath[i]){
          shortestPath[i] = tempShortest; // --> Take it
          route[i] = tempRoute;
          hasChanged = true;
        }
      }
      else if (shortestPath[i] != costs[i]){ //IF non with less cost and changes
        shortestPath[i] = costs[i]; //Take our direct cost instead
        route[i] = i;
        hasChanged = true;
      }
      tempShortest = RouterSimulator.INFINITY; //reset temp
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
  // Prints table and vectors in a nice way! 
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
  // Set new and send it
  public void updateLinkCost(int dest, int newcost) {
    costs[dest] = newcost; 
    sendPacketToNeighbours(myID);
  }

  // Send packet to all neighbors and maybe poison reverse
  private void sendPacketToNeighbours(int ID){
    for (int i = 0; i < neighbourID.size(); i++){
      int[] poisonShortestPath = new int[RouterSimulator.NUM_NODES];
      for (int d = 0; d < RouterSimulator.NUM_NODES; d++){
        if (route[d] == neighbourID.get(i) && usePoisonReverse){ //Poison reverse
          poisonShortestPath[d] = RouterSimulator.INFINITY; //Hinder node from returning to sender with inf. cost
        }
        else{
          poisonShortestPath[d] = shortestPath[d]; // No poison reverse, build as usual
        }
      }
      RouterPacket pkt = new RouterPacket(ID, neighbourID.get(i), poisonShortestPath);
      sendUpdate(pkt);
    }
  }
}

