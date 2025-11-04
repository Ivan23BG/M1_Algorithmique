import java.io.BufferedReader;
import java.io.FileReader;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.IntVar;

public class Expe {

	private static Model lireReseau(BufferedReader in) throws Exception{
			Model model = new Model("Expe");
			int nbVariables = Integer.parseInt(in.readLine());				// le nombre de variables
			int tailleDom = Integer.parseInt(in.readLine());				// la valeur max des domaines
			IntVar []var = model.intVarArray("x",nbVariables,0,tailleDom-1); 	
			int nbConstraints = Integer.parseInt(in.readLine());			// le nombre de contraintes binaires		
			for(int k=1;k<=nbConstraints;k++) { 
				String chaine[] = in.readLine().split(";");
				IntVar portee[] = new IntVar[]{var[Integer.parseInt(chaine[0])],var[Integer.parseInt(chaine[1])]}; 
				int nbTuples = Integer.parseInt(in.readLine());				// le nombre de tuples		
				Tuples tuples = new Tuples(new int[][]{},true);
				for(int nb=1;nb<=nbTuples;nb++) { 
					chaine = in.readLine().split(";");
					int t[] = new int[]{Integer.parseInt(chaine[0]), Integer.parseInt(chaine[1])};
					tuples.add(t);
				}
				model.table(portee,tuples).post();	
			}
			in.readLine();
			return model;
	}	
		
			
	public static void main(String[] args) throws Exception{
		String files_to_read[] = new String[] {"benchSatisf.txt", "benchInsat.txt"};
		// String ficName = "bench.txt";
		int nbRes=3;
		int nb_success = 0;
		double nb_total = 0;
		for (String ficName : files_to_read) {
			
		BufferedReader readFile = new BufferedReader(new FileReader(ficName));
		for(int nb=1 ; nb<=nbRes; nb++) {
			Model model=lireReseau(readFile);
			if(model==null) {
				System.out.println("Problème de lecture de fichier !\n");
				return;
			}
			System.out.println("Réseau lu dans "+ficName+" numero "+nb+" :\n"+model+"\n\n");

			
			model.getSolver().limitTime("10s");
			// Calcul de la première solution
			if(model.getSolver().solve()) {
				// System.out.println("\n\n*** Première solution ***");        
				// System.out.println(model);
				// on a trouvé une solution donc 
				// on augmente de 1 le nombre de reussites et de modeles
				nb_success += 1;
				nb_total += 1;
			} else if (model.getSolver().isStopCriterionMet()) {
				System.out.println("The solver could not find a solution nor prove that none exists in the given time");
			} else {
				System.out.println("The solver has proved the problem has no solution");
				// on a trouvé un modele qui n'a pas de solution
				nb_total += 1;
			}

			// Affichage de l'ensemble des caractéristiques de résolution
			// System.out.println("\n\n*** Bilan ***");        
			// model.getSolver().printStatistics();
		}
		double nb_reussites_percent = nb_success / nb_total * 100;
		System.out.println("Total de reussites: "+nb_reussites_percent+"%");
		}
		return;	
	}
	
}
