import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;


public class ReinesIntension {

	public static void main(String[] args) {
		
		// Création du modele
		Model model = new Model("Reines");
		
		
		// Création des variables
		IntVar [] reines = model.intVarArray("R", 8, 1, 8);

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
    model.allDifferent(reines[0], reines[1], reines[2], reines[3], reines[4], reines[5], reines[6], reines[7]).post();
    
    /*
     * Contrainte 2: Deux reines ne peuvent pas être sur la même ligne.
     */
    for (int i = 0; i < 8; i++) {
        for (int j = i + 1; j < 8; j++) {
            model.arithm(reines[i], "!=", reines[j]).post();
        }
    }

    /*
     * Contrainte 3: Deux reines ne peuvent pas être sur la même diagonale (de gauche à droite).
     */
    for (int i = 0; i < 8; i++) {
        for (int j = i + 1; j < 8; j++) {
            model.arithm(reines[i], "-", reines[j], "!=", i - j).post();
        }
    }

    /*
     * Contrainte 4: Deux reines ne peuvent pas être sur la même diagonale (de droite à gauche).
     */
    for (int i = 0; i < 8; i++) {
        for (int j = i + 1; j < 8; j++) {
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
