import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.constraints.extension.Tuples;


public class ZebreExtension {

	public static void main(String[] args) {
		
		// Création du modele
		Model model = new Model("Zebre");
		
		
		// Création des variables
		IntVar blu = model.intVar("Blue", 1, 5);	// blu est une variable entière dont le nom est "Blue" est le domaine [1,5]
		IntVar gre = model.intVar("Green", 1, 5)
		IntVar ivo = model.intVar("Ivory", 1, 5)
		IntVar red = model.intVar("Red", 1, 5)
		IntVar yel = model.intVar("Yellow", 1, 5)
		
		IntVar eng = model.intVar("English", 1, 5)
		IntVar jap = model.intVar("Japanese", 1, 5)
		IntVar nor = model.intVar("Norwegian", 1, 5)
		IntVar spa = model.intVar("Spanish", 1, 5)
		IntVar ukr = model.intVar("Ukrainian", 1, 5)
		
		IntVar cof = model.intVar("Coffee", 1, 5)
		IntVar mil = model.intVar("Milk", 1, 5)
		IntVar ora = model.intVar("Orange Juice", 1, 5)
		IntVar tea = model.intVar("Tea", 1, 5)
		IntVar wat = model.intVar("Water", 1, 5)
		
	    IntVar dog = model.intVar("Dog", 1, 5)
	    IntVar fox = model.intVar("Fox", 1, 5)
	    IntVar hor = model.intVar("Horse", 1, 5)
	    IntVar sna = model.intVar("Snail", 1, 5)
	    IntVar zeb = model.intVar("Zebra", 1, 5)
	    
	    IntVar che = model.intVar("Chesterfield", 1, 5)
	    IntVar koo = model.intVar("Kool", 1, 5)
	    IntVar luc = model.intVar("Lucky Strike", 1, 5)
	    IntVar old = model.intVar("Old Gold", 1, 5);
        IntVar par = model.intVar("Parliament", 1, 5);


        // Création des contraintes
        int [][] tEq = new int[][] {{1,1},{2,2},{3,3},{4,4},{5,5}};
        Tuples tuplesAutorises = new Tuples(tEq,true);		// création de Tuples de valeurs autorisés
        Tuples tuplesInterdits = new Tuples(tEq,false);		// création de Tuples de valeurs interdits
        
        model.table(new IntVar[]{blu,gre}, tuplesInterdits).post();
        // création d'une contrainte en extension de portée <blu,gre>
        // dont les tuples autorisés/interdits sont données par tuplesInterdits
        model.table(new IntVar[]{blu,ivo}, tuplesInterdits).post();
        model.table(new IntVar[]{blu,red}, tuplesInterdits).post();
        model.table(new IntVar[]{blu,yel}, tuplesInterdits).post();
        model.table(new IntVar[]{gre,ivo}, tuplesInterdits).post();
        model.table(new IntVar[]{gre,red}, tuplesInterdits).post();
        model.table(new IntVar[]{gre,yel}, tuplesInterdits).post();
        model.table(new IntVar[]{ivo,red}, tuplesInterdits).post();
        model.table(new IntVar[]{ivo,yel}, tuplesInterdits).post();
        model.table(new IntVar[]{red,yel}, tuplesInterdits).post();

        model.table(new IntVar[]{eng,jap}, tuplesInterdits).post();
        model.table(new IntVar[]{eng,nor}, tuplesInterdits).post();
        model.table(new IntVar[]{eng,spa}, tuplesInterdits).post();
        model.table(new IntVar[]{eng,ukr}, tuplesInterdits).post();
        model.table(new IntVar[]{jap,nor}, tuplesInterdits).post();
        model.table(new IntVar[]{jap,spa}, tuplesInterdits).post();
        model.table(new IntVar[]{jap,ukr}, tuplesInterdits).post();
        model.table(new IntVar[]{nor,spa}, tuplesInterdits).post();
        model.table(new IntVar[]{nor,ukr}, tuplesInterdits).post();
        model.table(new IntVar[]{spa,ukr}, tuplesInterdits).post();

        model.table(new IntVar[]{cof,mil}, tuplesInterdits).post();
        model.table(new IntVar[]{cof,ora}, tuplesInterdits).post();
        model.table(new IntVar[]{cof,tea}, tuplesInterdits).post();
        model.table(new IntVar[]{cof,wat}, tuplesInterdits).post();
        model.table(new IntVar[]{mil,ora}, tuplesInterdits).post();
        model.table(new IntVar[]{mil,tea}, tuplesInterdits).post();
        model.table(new IntVar[]{mil,wat}, tuplesInterdits).post();
        model.table(new IntVar[]{ora,tea}, tuplesInterdits).post();
        model.table(new IntVar[]{ora,wat}, tuplesInterdits).post();
        model.table(new IntVar[]{tea,wat}, tuplesInterdits).post();

        model.table(new IntVar[]{dog,fox}, tuplesInterdits).post();
        model.table(new IntVar[]{dog,hor}, tuplesInterdits).post();
        model.table(new IntVar[]{dog,sna}, tuplesInterdits).post();
        model.table(new IntVar[]{dog,zeb}, tuplesInterdits).post();
        model.table(new IntVar[]{fox,hor}, tuplesInterdits).post();
        model.table(new IntVar[]{fox,sna}, tuplesInterdits).post();
        model.table(new IntVar[]{fox,zeb}, tuplesInterdits).post();
        model.table(new IntVar[]{hor,sna}, tuplesInterdits).post();
        model.table(new IntVar[]{hor,zeb}, tuplesInterdits).post();
        model.table(new IntVar[]{sna,zeb}, tuplesInterdits).post();

        model.table(new IntVar[]{che,koo}, tuplesInterdits).post();
        model.table(new IntVar[]{che,luc}, tuplesInterdits).post();
        model.table(new IntVar[]{che,old}, tuplesInterdits).post();
        model.table(new IntVar[]{che,par}, tuplesInterdits).post();
        model.table(new IntVar[]{koo,luc}, tuplesInterdits).post();
        model.table(new IntVar[]{koo,old}, tuplesInterdits).post();
        model.table(new IntVar[]{koo,par}, tuplesInterdits).post();
        model.table(new IntVar[]{luc,old}, tuplesInterdits).post();
        model.table(new IntVar[]{luc,par}, tuplesInterdits).post();
        model.table(new IntVar[]{old,par}, tuplesInterdits).post();

        
        /************************************************************************
         *                                                                      *
         * Compléter en ajoutant les contraintes modélisant les phrases 2 à 15  *
         *                                                                      *
         ************************************************************************/

        /*
         * Contrainte 2: The Englisman lives in the red house.
         */
        model.table(new IntVar[]{eng,red}, tuplesAutorises).post();

        /*
         * Contrainte 3: The Spaniard owns the dog.
         */
        model.table(new IntVar[]{spa,dog}, tuplesAutorises).post();

        /*
         * Contrainte 4: Coffee is drunk in the green house.
         */
        model.table(new IntVar[]{cof,gre}, tuplesAutorises).post();

        /*
         * Contrainte 5: The Ukrainian drinks tea.
         */
        model.table(new IntVar[]{ukr,tea}, tuplesAutorises).post();

        /*
         * Contrainte 6: The green house is immediately to the right of the ivory house.
         */
        int [][] tc6 = new int[][] {{1,2},{2,3},{3,4},{4,5}};
        Tuples ta6 = new Tuples(tc6,true);
        model.table(new IntVar[]{ivo,gre}, ta6).post();

        /*
         * Contrainte 7: The Old Gold smoker owns snails.
         */
        model.table(new IntVar[]{old,sna}, tuplesAutorises).post();

        /*
         * Contrainte 8: Kools are smoked in the yellow house.
         */
        model.table(new IntVar[]{koo,yel}, tuplesAutorises).post();

        /*
         * Contrainte 9: Milk is drunk in the middle house.
         */
        IntVar ho3 = model.intVar("House 3", 3, 3);
        model.table(new IntVar[]{mil, ho3}, tuplesAutorises).post();

        /*
         * Contrainte 10: The Norwegian lives in the first house.
         */
        IntVar ho1 = model.intVar("House 1", 1, 1);
        model.table(new IntVar[]{nor, ho1}, tuplesAutorises).post();

        /*
         * Contrainte 11: The man who smokes Chesterfields lives in the house next to the man with the fox.
         */
        int [][] tc11 = new int[][] {{1,2},{2,1}, {2, 3}, {3, 2}, {3, 4}, {4, 3}, {4, 5}, {5, 4}};
        Tuples ta11 = new Tuples(tc11,true);
        model.table(new IntVar[]{che,fox}, ta11).post();

        /*
         * Contrainte 12: Kools are smoked in the house next to the house where the horse is kept.
         */
        int [][] tc12 = new int[][] {{1,2},{2,1}, {2, 3}, {3, 2}, {3, 4}, {4, 3}, {4, 5}, {5, 4}};
        Tuples ta12 = new Tuples(tc12,true);
        model.table(new IntVar[]{koo,hor}, ta12).post();

        /*
         * Contrainte 13: The Lucky Strike smoker drinks orange juice.
         */
        model.table(new IntVar[]{luc,ora}, tuplesAutorises).post();

        /*
         * Contrainte 14: The Japanese smokes Parliaments.
         */
        model.table(new IntVar[]{jap,par}, tuplesAutorises).post();

        /*
         * Contrainte 15: The Norwegian lives next to the blue house.
         */
        int [][] tc15 = new int[][] {{1,2},{2,1}, {2, 3}, {3, 2}, {3, 4}, {4, 3}, {4, 5}, {5, 4}};
        Tuples ta15 = new Tuples(tc15,true);
        model.table(new IntVar[]{nor,blu}, ta15).post();
        
        // Affichage du réseau de contraintes créé
        System.out.println("*** Réseau Initial ***");
        System.out.println(model);
        

        // Calcul de la première solution
        if(model.getSolver().solve()) {
        	System.out.println("\n\n*** Première solution ***")
        	System.out.println(model);
        }

        
/*
    	// Calcul de toutes les solutions
    	System.out.println("\n\n*** Autres solutions ***")
        while(model.getSolver().solve()) {    	
            System.out.println("Sol "+ model.getSolver().getSolutionCount()+"\n"+model);
	    }
*/
 
        
        // Affichage de l'ensemble des caractéristiques de résolution
      	System.out.println("\n\n*** Bilan ***")
        model.getSolver().printStatistics();
	}
}
