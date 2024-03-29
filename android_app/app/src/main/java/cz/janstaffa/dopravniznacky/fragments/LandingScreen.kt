package cz.janstaffa.dopravniznacky.fragments

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.Navigation
import cz.janstaffa.dopravniznacky.R
import cz.janstaffa.dopravniznacky.databinding.FragmentLandingScreenBinding


class LandingScreen : Fragment() {
    private var landingScreenBinding: FragmentLandingScreenBinding? = null


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
    }

    override fun onDestroyView() {
        landingScreenBinding = null
        super.onDestroyView()
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        landingScreenBinding = FragmentLandingScreenBinding.inflate(inflater, container, false)
        return landingScreenBinding!!.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        landingScreenBinding!!.continueToAppBtn.setOnClickListener {
            Navigation.findNavController(requireActivity(), R.id.fragment_container).navigate(
                LandingScreenDirections.actionLandingScreenToCameraFragment()
            )

        }

        landingScreenBinding!!.aboutBtn.setOnClickListener {
            val uri = Uri.parse(ABOUT_URL)
            val intent = Intent(Intent.ACTION_VIEW, uri)
            startActivity(intent)
        }
    }
    companion object {
        const val ABOUT_URL = "https://github.com/janstaffa/dopravni-znacky"
    }
}