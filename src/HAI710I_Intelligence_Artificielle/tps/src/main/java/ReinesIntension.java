import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;


public class ReinesIntension {

	public static void main(String[] args) {
		
		// Création du modele
		Model model = new Model("Reines");
		
		
		// Création des variables
    int [] vals_possibles = {1, 2, 3, 4, 8, 12, 16};
    
    //int n = 8; // default n value
    for (int val : vals_possibles) {
        int n = val;
        System.out.println("\n\nRésolution du problème des " + val + " reines");
        model = new Model("Reines"); // reset model for next iteration
    
		
    
    IntVar [] reines = model.intVarArray("R", n, 1, n);

    // Création des contraintes
    // Le allDiff est déjà dans la construction même du tableau de reines
    /*****************************************************************
     *                                                                      *
     * Compléter en ajoutant les contraintes modélisant les phrases 1 à 4   *
     *                                                                      *
     ************************************************************************/
    
    
    /*
     * Contrainte 1: Deux reines ne peuvent pas être sur la même colonne.
     */
    model.allDifferent(reines).post();
    
    /*
     * Contrainte 2: Deux reines ne peuvent pas être sur la même ligne.
     */
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            model.arithm(reines[i], "!=", reines[j]).post();
        }
    }

    /*
     * Contrainte 3: Deux reines ne peuvent pas être sur la même diagonale (de gauche à droite).
     */
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            model.arithm(reines[i], "-", reines[j], "!=", i - j).post();
        }
    }

    /*
     * Contrainte 4: Deux reines ne peuvent pas être sur la même diagonale (de droite à gauche).
     */
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            model.arithm(reines[i], "-", reines[j], "!=", j - i).post();
        }
    }
    
    // Affichage du réseau de contraintes créé
    System.out.println("*** Réseau Initial ***");
    System.out.println(model);
    

    // Calcul de la première solution
    if(model.getSolver().solve()) {
      System.out.println("\n\n*** Première solution ***");        
      System.out.println(model);
    }

        
/*        
    // Calcul de toutes les solutions
    System.out.println("\n\n*** Autres solutions ***");        
      while(model.getSolver().solve()) {    	
          System.out.println("Sol "+ model.getSolver().getSolutionCount()+"\n"+model);
    }
*/	    
 
        
    // Affichage de l'ensemble des caractéristiques de résolution
    System.out.println("\n\n*** Bilan ***");        
    model.getSolver().printStatistics();
	}
}
}

// on peut alors constater que le nombre de solutions 
// pour tout n est toujours 1 à rotation près